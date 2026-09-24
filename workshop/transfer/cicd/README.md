# Od notebooka do potoku: szkielet CI/CD

Materiał **do zabrania do siebie**, nie ćwiczenie warsztatowe. Na sali nie ma na to czasu,
a bez własnego repozytorium i service principala i tak nie dałoby się tego przejść uczciwie.

## Po co to jest

W M5 zbudowałeś macierz tras: pytanie → oczekiwane narzędzie → wynik ✅/❌. Na warsztacie
uruchamiasz ją ręcznie. W produkcji ta sama macierz powinna być **bramką**: jeśli agent
przestaje wybierać właściwe narzędzia, wdrożenie się nie wykonuje.

To jest cała różnica między „agent działał, gdy go pisałem" a „wiem, że agent nadal działa".

## Co tu jest

| Plik | Rola |
| --- | --- |
| `databricks.yml` | Asset Bundle: zmienne, cele `dev` i `prod`, zadanie `agent_gate` |
| `.github/workflows/agent-gate.yml` | GitHub Actions: walidacja bundle → macierz tras → wdrożenie tylko po zielonej bramce |

## Czego brakuje i dlaczego

Szkielet celowo **nie jest kompletny** — te decyzje zależą od Twojego środowiska:

- **próg bramki** (`min_routes_ok`): ile tras musi się zgadzać. Macierz bywa niestabilna
  między przebiegami, więc próg 6/6 zablokuje Ci wdrożenia. Zacznij od 5/6 i obserwuj;
- **tożsamość** (`agent_service_principal`): w produkcji agent nie działa z Twoimi
  uprawnieniami. Sprawdzone na warsztacie (M6): service principal z samym `EXECUTE`
  na funkcjach, **bez** `SELECT` na tabelach, wywołuje je poprawnie;
- **co po wdrożeniu**: bramka sprawdza agenta przed, monitoring sprawdza go po.
  Scorery na próbce ruchu (M6, tabela „przed produkcją") to osobny krok;
- **koszt**: rachunek z M5 (`m5-cost`) przelicz na swoją skalę, zanim wdrożysz.

## Pułapka, na którą trafiliśmy przy próbach

`CREATE OR REPLACE FUNCTION` **kasuje wszystkie granty na funkcji**. Jeśli potok
odtwarza funkcje przy każdym wdrożeniu, musi też odtwarzać uprawnienia — inaczej agent
straci dostęp do własnych narzędzi po pierwszym deployu. Nadawaj je w skrypcie
wdrożeniowym, nie ręcznie.
