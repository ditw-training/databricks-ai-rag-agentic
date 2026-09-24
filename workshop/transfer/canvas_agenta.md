# Canvas agenta: przenieś wzorzec na nowe dane

Jedna strona, uzupełniana przez cały dzień. Po każdym module dopisz jeden wiersz. Na capstone (M5+) przepisujesz ją do kodu w notebooku `m5b_transfer_capstone`.

**Moja domena (jedno zdanie):**

**Kto zadaje pytania i po co:**

**Dane na capstone:** ☐ Bakehouse (`samples.bakehouse`, domyślnie dla wszystkich; po ścieżce B z Twoimi trasami z M5) ☐ Airbnb (`workspace.airbnb.listings`, C · Wyzwanie, gdy agent piekarni już działa)

Tabele i funkcja z capstone trafią do schematu Twoich danych: `workspace.bakehouse` albo `workspace.airbnb`.

---

## M0–M1 · Pytania i zasady

**5 pytań, które użytkownik naprawdę zada:**
1.
2.
3.
4.
5.

**System prompt, wersja 1**
- Co robić (domena, język, skąd liczby):
- Czego nie robić (dane wrażliwe w **mojej** domenie):
- Jak odmawiać (alternatywa, „nie mam takich danych”):

## M2 · Narzędzia tabelaryczne

| Pytanie (nr) | Nazwa funkcji | Parametr | `COMMENT`: kiedy użyć / kiedy nie | Czego nie zwraca |
|---|---|---|---|---|
| | | | | |
| | | | | |

## M3 · Dokumenty

| Jakie dokumenty lub teksty | Typowa długość sekcji | Dzielić na fragmenty? (rozmiar) | Metadane do cytatów i filtrów |
|---|---|---|---|
| | | | |

## M4 · Dane wrażliwe i dostęp

| Kolumna | Dlaczego wrażliwa | Decyzja: nie kopiuj / maska / filtr wierszy | Kto widzi wartość (grupa) |
|---|---|---|---|
| | | | |

Pytania ad hoc dla Genie (a nie dla funkcji):

## M5 · Macierz tras

| Pytanie | Oczekiwana trasa (narzędzie / odmowa / fallback) | Dlaczego |
|---|---|---|
| | | |
| | | |
| | | |

Zdanie „do czego **nie** używać” dla każdego narzędzia:

Jeśli w M5 zrobiłeś ścieżkę B, cztery przypadki dla agenta piekarni są już w tabeli `workspace.bakehouse.route_cases`. Capstone wczyta je przy `DATA_OPTION = "bakehouse"`.

## M5+ · Karta wyjściowa

Ten Canvas przepisujesz do kodu w ZADANIU K1, a funkcję z sekcji M2 piszesz w ZADANIU K2.

- Trasy zgodne: ___ / 3 (zrzut ekranu macierzy)
- Wzorzec, który przeniosłem, to:
- Jedna rzecz, którą poprawiłem (COMMENT / opis narzędzia / prompt), to:

## M6 · Do PoC na moich danych brakuje

☐ dostęp do prawdziwych danych ☐ właściciel biznesowy ☐ zestaw pytań testowych z oczekiwanymi trasami ☐ tożsamość agenta (service principal) i minimalne uprawnienia ☐ guardrails na endpoincie ☐ monitoring

---

**Zasada na dziś:** pracujemy wyłącznie na danych z repozytorium i katalogu `samples`. Na Free Edition nie wgrywamy żadnych danych firmowych ani osobowych.
