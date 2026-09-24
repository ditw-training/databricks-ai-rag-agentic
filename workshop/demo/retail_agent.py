"""Agent TechRetail w postaci, w jakiej trafia do Unity Catalog.

To jest wzorzec do skopiowania dla własnego agenta. Uczestnik kopiuje ten plik w capstonie
i podmienia trzy rzeczy: listę funkcji, opis narzędzia wyszukiwania i system prompt. Reszta —
budowa agenta, interfejs `ResponsesAgent`, streaming — zostaje bez zmian.

MLflow rejestruje modele „z kodu”: do rejestru idzie TEN plik, a nie obiekt z pamięci notebooka.
Dzięki temu kod agenta jest zwykłym Pythonem — z kolorowaniem, sprawdzaniem składni i historią
w gicie — a nie tekstem w zmiennej. Konfiguracja (endpoint, prompt, lista funkcji) przychodzi
z `model_config` przekazanego przy `log_model`, więc ten sam plik obsługuje każdy wariant agenta.
"""
from typing import Generator
from uuid import uuid4

import mlflow
from databricks_langchain import ChatDatabricks, UCFunctionToolkit, VectorSearchRetrieverTool
from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, ToolMessage
from mlflow.models import ModelConfig
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)

config = ModelConfig()

# Odpowiednik dawnego max_iterations=6: jedna tura agenta to węzeł modelu i węzeł narzędzi,
# więc limit rekurencji grafu jest dwa razy większy niż liczba tur.
RECURSION_LIMIT = 12


def build_agent():
    """Ten sam agent co w notebooku: funkcje Unity Catalog plus wyszukiwanie w raportach."""
    rag_tool = VectorSearchRetrieverTool(
        index_name=config.get("search_index"),
        tool_name="search_retail_reports",
        tool_description=config.get("rag_tool_description"),
        num_results=4,
    )
    tools = UCFunctionToolkit(function_names=config.get("function_names")).tools + [rag_tool]
    return create_agent(
        model=ChatDatabricks(endpoint=config.get("llm_endpoint"), temperature=0.1),
        tools=tools,
        system_prompt=config.get("system_prompt"),
    )


def tools_used(state: dict) -> list:
    """Krótkie nazwy narzędzi, po które agent sięgnął w tej odpowiedzi."""
    return [message.name.split("__")[-1] for message in state["messages"]
            if isinstance(message, ToolMessage)]


class RetailAgent(ResponsesAgent):
    """Standardowy interfejs agenta: rozumieją go Playground, Databricks Apps i ewaluacja."""

    def __init__(self):
        self.agent = build_agent()

    @staticmethod
    def _state(request: ResponsesAgentRequest) -> dict:
        """Wejście Responses API to lista wiadomości i stan agenta LangGraph też nią jest.

        Rolę `system` pomijamy: prompt systemowy wnosi `create_agent`, a druga kopia
        tylko zabierałaby miejsce w oknie kontekstu.
        """
        messages = [item.model_dump() for item in request.input]
        return {"messages": [{"role": message["role"], "content": message["content"]}
                             for message in messages
                             if message.get("role") in ("user", "assistant")
                             and isinstance(message.get("content"), str)]}

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        state = self.agent.invoke(self._state(request),
                                  config={"recursion_limit": RECURSION_LIMIT})
        answer = str(state["messages"][-1].content)
        return ResponsesAgentResponse(
            output=[self.create_text_output_item(text=answer, id=str(uuid4()))],
            custom_outputs={"tools": tools_used(state)},
        )

    def predict_stream(
        self, request: ResponsesAgentRequest
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        """Odpowiedź po kawałku: tego oczekują Playground i czat w Databricks Apps.

        Bez tej metody klient czeka w ciszy do końca całej pętli agenta, a przy dwóch
        wywołaniach modelu i narzędziu po drodze to kilkanaście sekund pustego ekranu.
        """
        item_id, answer = str(uuid4()), ""
        for chunk, _metadata in self.agent.stream(
            self._state(request),
            stream_mode="messages",
            config={"recursion_limit": RECURSION_LIMIT},
        ):
            is_text = isinstance(chunk, AIMessageChunk) and isinstance(chunk.content, str)
            if is_text and chunk.content:
                answer += chunk.content
                yield ResponsesAgentStreamEvent(
                    **self.create_text_delta(delta=chunk.content, item_id=item_id)
                )
        yield ResponsesAgentStreamEvent(
            type="response.output_item.done",
            item=self.create_text_output_item(text=answer, id=item_id),
        )


mlflow.langchain.autolog()
mlflow.models.set_model(RetailAgent())
