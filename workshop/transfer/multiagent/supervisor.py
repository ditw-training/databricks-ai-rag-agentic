"""Supervisor z dwoma subagentami, zbudowany na macierzy tras z M5.

Materiał do zabrania do siebie. Na warsztacie budujemy jednego agenta z listą
narzędzi, a Supervisor Agenta oglądamy w M6 jako pokaz w interfejsie. Ten plik
pokazuje to samo w kodzie, żeby dało się zajrzeć do środka.

Uruchomienie: notebook w Databricks, serverless, environment_version 5.
    %pip install -U -qqqq databricks-langchain langchain langgraph langchain-core mlflow
    dbutils.library.restartPython()

Wzorzec nazywa się "agent jako narzędzie". Każdy subagent jest pełnym agentem
z własną pętlą i własnymi narzędziami, a supervisor dostaje go jako zwykłe
narzędzie. Dokładnie to robi Agent Bricks Supervisor w panelu
"Tools and sub-agents", tylko bez pisania kodu.
"""

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool
from databricks_langchain import ChatDatabricks

import mlflow

mlflow.langchain.autolog()

CATALOG = "workspace"
SCHEMA = "default"
LLM_ENDPOINT = "databricks-claude-sonnet-4-5"

llm = ChatDatabricks(endpoint=LLM_ENDPOINT, temperature=0)


# Jedna tura agenta to węzeł modelu i węzeł narzędzi, więc limit rekurencji grafu
# jest dwa razy większy niż liczba tur (odpowiednik dawnego max_iterations=5).
RECURSION_LIMIT = 10


def build_agent(system_prompt: str, tools: list):
    """Zwykły agent z M5. Supervisor i każdy subagent są tą samą konstrukcją."""
    return create_agent(model=llm, tools=tools, system_prompt=system_prompt)


def ask(agent, pytanie: str) -> dict:
    """Jedno wywołanie: wchodzi pytanie, wychodzi stan grafu z listą wiadomości."""
    return agent.invoke({"messages": [{"role": "user", "content": pytanie}]},
                        config={"recursion_limit": RECURSION_LIMIT})


def answer_of(state: dict) -> str:
    return str(state["messages"][-1].content)


# --- Subagent 1: liczby -------------------------------------------------------
# Podstaw tu swoje narzędzia z M2 (funkcje Unity Catalog przez UCFunctionToolkit).
NUMBERS_TOOLS: list = []

numbers_agent = build_agent(
    "Odpowiadasz wyłącznie na pytania o liczby z tabel. "
    "Każdą liczbę bierzesz z wyniku narzędzia. Niczego nie zgadujesz. "
    "Jeśli narzędzie nie zwróciło danych, napisz, że ich nie masz.",
    NUMBERS_TOOLS,
)

# --- Subagent 2: treść dokumentów --------------------------------------------
# Podstaw tu swoje narzędzie RAG z M3 (retriever nad indeksem AI Search).
DOCS_TOOLS: list = []

docs_agent = build_agent(
    "Odpowiadasz wyłącznie na pytania o treść raportów. "
    "Do każdego twierdzenia podajesz źródło z wyniku wyszukiwania. "
    "Jeśli wyszukiwanie nic nie zwróciło, powiedz to wprost zamiast zmyślać.",
    DOCS_TOOLS,
)


# --- Supervisor ---------------------------------------------------------------
# Opisy poniżej to dokładnie kolumna "dlaczego" z Twojej macierzy tras z M5.
# Zdanie "do czego NIE używać" działa tu tak samo jak przy zwykłym narzędziu.

def ask_numbers(pytanie: str) -> str:
    return answer_of(ask(numbers_agent, pytanie))


def ask_docs(pytanie: str) -> str:
    return answer_of(ask(docs_agent, pytanie))


SUPERVISOR_TOOLS = [
    StructuredTool.from_function(
        func=ask_numbers,
        name="agent_liczby",
        description=(
            "Pytania o wartości liczbowe z tabel: liczba klientów, przychód, średnie. "
            "NIE używaj do pytań o treść raportów ani o powody zjawisk."
        ),
    ),
    StructuredTool.from_function(
        func=ask_docs,
        name="agent_dokumenty",
        description=(
            "Pytania o to, co napisano w raportach: wnioski, rekomendacje, przyczyny. "
            "NIE używaj do pytań o konkretne liczby z tabel."
        ),
    ),
]

supervisor = build_agent(
    "Jesteś koordynatorem. Sam nie odpowiadasz na pytania merytoryczne. "
    "Rozdzielasz pytanie między subagentów i scalasz ich odpowiedzi w jedną. "
    "Pytanie złożone rozbij na części i zadaj każdą właściwemu subagentowi. "
    "Liczby podajesz wyłącznie z odpowiedzi subagentów. "
    "Nigdy nie ujawniasz danych osobowych klientów.",
    SUPERVISOR_TOOLS,
)


# --- Macierz tras, ta sama co w M5, z jedną nową kolumną ----------------------
# W systemie z jednym agentem zła odpowiedź ma jedną przyczynę: zły opis narzędzia.
# Tutaj przyczyny są dwie, więc test musi rozróżniać, KTÓRY poziom wybrał źle.

ROUTES = [
    {"pytanie": "Ilu mamy klientów VIP?", "oczekiwany_subagent": "agent_liczby"},
    {"pytanie": "Co raporty mówią o retencji VIP?", "oczekiwany_subagent": "agent_dokumenty"},
    {"pytanie": "Ilu mamy klientów VIP i co raporty mówią o ich retencji?",
     "oczekiwany_subagent": "oba"},
]


def run_matrix() -> None:
    for case in ROUTES:
        with mlflow.start_span(name="supervisor_case") as span:
            span.set_attribute("pytanie", case["pytanie"])
            stan = ask(supervisor, case["pytanie"])
        # Każde wykonane narzędzie zostawia w stanie ToolMessage z nazwą subagenta.
        uzyte = [m.name for m in stan["messages"] if isinstance(m, ToolMessage)]
        print(f"{case['pytanie']}\n  oczekiwano: {case['oczekiwany_subagent']}"
              f"\n  wywołano:   {uzyte or 'nic'}")
        print("  Gdy trasa jest zła, sprawdź w tej kolejności:")
        print("    1. czy supervisor wybrał właściwego subagenta (popraw opisy w SUPERVISOR_TOOLS)")
        print("    2. czy subagent wybrał właściwe narzędzie (popraw COMMENT funkcji)")


if __name__ == "__main__":
    run_matrix()
