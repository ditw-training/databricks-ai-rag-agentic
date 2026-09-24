# Supervisor z subagentami: szkielet do zabrania

Materiał **do zabrania do siebie**, nie ćwiczenie warsztatowe. Na warsztacie budujesz
jednego agenta z listą narzędzi, a Supervisor Agenta oglądasz w M6 jako pokaz
w interfejsie. Ten katalog pokazuje to samo w kodzie.

## Po co to jest

Wrócisz do firmy i ktoś zapyta: „a multi-agent robimy?". Ten plik jest odpowiedzią,
którą da się uruchomić, oraz materiałem do odpowiedzi „jeszcze nie i oto dlaczego".

## Co tu jest

| Plik | Rola |
| --- | --- |
| `supervisor.py` | supervisor z dwoma subagentami, zbudowany na macierzy tras z M5 |

Wzorzec nazywa się **agent jako narzędzie**. Każdy subagent jest pełnym agentem
z własną pętlą, a supervisor dostaje go jako zwykłe narzędzie. To samo robi panel
*Tools and sub-agents* w Agent Bricks, tylko bez kodu.

## Co przenosisz z warsztatu bez zmian

Macierz tras z M5 jest gotową specyfikacją supervisora. Nazwa trasy staje się nazwą
subagenta, kolumna „dlaczego" staje się jego `description`, a oczekiwana trasa
zostaje testem. Zdanie „do czego NIE używać" działa na poziomie subagenta tak samo
jak na poziomie pojedynczego narzędzia.

Dwa miejsca w `supervisor.py` są puste i czekają na Twoje narzędzia: `NUMBERS_TOOLS`
(funkcje Unity Catalog z M2) i `DOCS_TOOLS` (retriever nad indeksem AI Search z M3).

## Co się zmienia względem jednego agenta

Zła odpowiedź ma teraz dwie możliwe przyczyny zamiast jednej. Supervisor mógł wybrać
złego subagenta albo subagent mógł wybrać złe narzędzie. Dlatego `run_matrix()`
wypisuje kolejność sprawdzania, a nie samo ✅ albo ❌. Bez tego rozróżnienia
poprawiasz na oślep.

Ślad w MLflow też się rozdziela. Trace supervisora pokazuje wybór subagenta,
a osobne ślady pokazują, co robił każdy subagent w środku.

## Zanim to wdrożysz: rachunek

Jedno pytanie do supervisora to wywołanie modelu na wybór subagenta plus pełna pętla
każdego wywołanego subagenta. Komórka `m5-cost` z warsztatu wypisuje, ile wywołań
modelu przypada na pytanie u Ciebie. Przemnóż rachunek miesięczny z tej komórki
przez liczbę, którą dołoży supervisor, zanim zaczniesz rozmowę o wdrożeniu.

## Kiedy tego nie robić

Jeśli narzędzia mieszczą się w jednym prompcie i utrzymuje je jeden zespół,
supervisor dokłada koszt i drugie miejsce do debugowania, a nie zdolność.

Sięgnij po niego, gdy subagent już istnieje jako osobny produkt z własną logiką
(Genie Agent ma własną pętlę generowania SQL, więc opakowanie go jest tańsze niż
odtwarzanie) albo gdy różne zespoły odpowiadają za różne agenty i nie chcesz
scalać ich w jeden prompt.

## Obserwacja z warsztatu, o której warto pamiętać

W pokazie w M6 Supervisor wywołuje dwa subagenty równolegle. Jeden z nich,
Knowledge Assistant, nie zwraca wyników — sprawdziliśmy to na trzech asystentach
i dwóch workspace'ach. Supervisor sam sięgnął wtedy po indeks AI Search, dodany
jako osobny klocek, i odpowiedź mimo wszystko powstała.

To jest cała nauka o odporności w systemie z wieloma agentami. Nie bierze się ona
z braku awarii, tylko z tego, że to samo zadanie ma drugą drogę. Kosztuje za to
dodatkowe wywołania, więc planuj ją świadomie, a nie przy okazji.
