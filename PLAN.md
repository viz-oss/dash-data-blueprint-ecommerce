# 0. Główny Dashboard
*Sekcja początkowa dająca natychmiastowy, syntetyczny wgląd w ogólną kondycję biznesu bez konieczności zagłębiania się w szczegółowe raporty.*
Tylko nie wiem jak to jeszcze dokładnie zrobić

## Podstrony dostępne po kliknięciu:
1. Analiza produktów
2. Analiza finansów
3. Analiza magazynu
4. Analiza klientów
5. Analiza Allegro Ads
6. Analiza konkurencji
7. Analiza zwrotów i reklamacji
8. Prognozy AI
9. Alerty

# 1. Analiza produktów:
## Ocena produktów
Stworzenie kompleksowego modułu oceny produktów, który pozwoli szybko zidentyfikować najlepiej oraz najsłabiej radzące sobie produkty. Analiza będzie oparta na kilku niezależnych rankingach, a następnie połączona w jeden końcowy wynik produktu.

### Szczegółowe rankingi
Dla każdego produktu zostaną utworzone rankingi w następujących kategoriach:

- Najlepiej sprzedające się (liczba sprzedanych sztuk)
- Największy przychód
- Najwyższa marża / zysk (Cena sprzedaży − Koszt zakupu)
- Największy wzrost sprzedaży (procentowy wzrost sprzedaży)
- Najwyżej oceniane przez klientów

Każdy ranking będzie prezentował wybraną przez użytkownika ilość produktów w danej kategorii, aby umożliwić porównanie ich z pozostałymi.

### Główny ranking produktów
Na podstawie wyników ze wszystkich kategorii zostanie wyliczony **ogólny wynik produktu**.
Każdy produkt otrzyma ocenę w skali **1–100 punktów**, która będzie odzwierciedlać jego ogólną efektywność sprzedażową.

#### Wagi poszczególnych kryteriów
| Kryterium | Waga |
|-----------|------:|
| Liczba sprzedanych sztuk | 25% |
| Wartość sprzedaży | 20% |
| Marża / zysk | 20% |
| Dynamika wzrostu sprzedaży | 15% |
| Średnia ocen klientów | 10% |
| Współczynnik zwrotów | 10% |

### AI rekomendacje
Najważniejsze wnioski, rekomendacje co warto zmienić/zrobić

## 2. Analiza finansów
Zapewnienie pełnego obrazu kondycji finansowej sklepu poprzez analizę przychodów, kosztów, rentowności oraz zmian w czasie. Moduł ma pomóc właścicielowi ocenić, czy działalność jest opłacalna oraz wskazać obszary wymagające optymalizacji.

### 2.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi w danym momencie
- Łączny przychód 
- Łączne koszty
- Zysk brutto
- Marża całkowita
- Średnia wartość zamówienia

### 2.2 Szczegółowe analizy
#### 2.2.1 Przychody
- wykres przychodów z z możliwośćia modulacji analizowanego czasu
- przychody dzienne, tygodniowe i miesięczne,
- identyfikację okresów największej i najmniejszej sprzedaży,
- analizę trendów.

Analiza AI:
- wzrosty i spadki przychodów względem poprzednich okresów,
- okresy o najwyższej i najniższej sprzedaży,
- sezonowe trendy sprzedażowe,
- nagłe odchylenia od standardowego poziomu przychodów,
- prognozowany przychód na podstawie aktualnego trendu,
- wpływ liczby zamówień oraz średniej wartości koszyka na zmianę przychodów.
  
#### 2.2.2 Koszty
Dashboard kosztów:
- Łączne koszty w wybranym okresie
- Zmiana kosztów względem poprzedniego okresu (%)
- Wykres kosztów z możliwością wyboru zakresu czasu
  - dzień
  - tydzień
  - miesiąc
  - rok

Podział wszystkich kosztów na kategorie:
- Koszt zakupu towarów
- Koszty dostawy
- Prowizje platform sprzedażowych (np. Allegro)
- Koszty reklam
- Pozostałe koszty operacyjne

Dla każdej kategorii prezentowane będą:
- całkowita wartość kosztów,
- udział procentowy w kosztach całkowitych,
- zmiana względem poprzedniego okresu,
- trend kosztów w czasie.

Analiza AI
System automatycznie wykrywa:
- kategorie kosztów rosnące najszybciej,
- nietypowe wzrosty wydatków,
- największe źródła kosztów,
- nagłe zmiany kosztów w wybranym okresie.

#### 2.2.3 Rentowność

- wykres zysku brutto i marży w czasie,
- porównanie zysku względem poprzednich okresów,
- analiza zmian rentowności,
- wpływ kosztów na końcowy wynik finansowy.

Analiza AI
System automatycznie wykrywa:
- spadek lub wzrost rentowności,
- sytuacje, w których wzrost sprzedaży nie przekłada się na wzrost zysku,
- gwałtowny wzrost kosztów obniżający marżę,
- okresy najwyższej i najniższej rentowności.

## 3. Analiza magazynu
Monitorowanie stanu magazynowego oraz dostępności produktów w celu zapewnienia ciągłości sprzedaży i ograniczenia kosztów związanych z nadmiarem lub brakiem towaru.

### 3.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi:
- Łączna liczba wystawionych produktów
- Łączna liczba dostępnych sztuk w magazynie
- Liczba produktów z niskim stanem magazynowym
- Liczba produktów niedostępnych

### 3.2 Szczegółowe analizy
#### 3.2.1 Stan magazynowy
- liczba aktywnych ofert,
- liczba produktów dostępnych do sprzedaży,
- liczba produktów niedostępnych,

#### 3.2.2 Produkty wymagające uwagi
Lista produktów:
- z niskim stanem magazynowym,
- niedostępnych,
- których zapas szybko się zmniejsza,
- zalegających w magazynie przez długi czas.

### 3.3 Analiza AI
System automatycznie wykrywa:
- produkty, których zapas wkrótce się wyczerpie,
- produkty zalegające w magazynie,
- nietypowo szybki spadek stanów magazynowych,
- produkty o zbyt dużym zapasie względem sprzedaży,
- prognozowany termin wyczerpania zapasów.

## 4. Analiza klientów
Analiza zachowań klientów w celu lepszego zrozumienia ich aktywności, lojalności oraz wartości dla sklepu. Moduł ma wspierać podejmowanie działań zwiększających sprzedaż i utrzymanie klientów.

### 4.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi:
- Łączna liczba klientów
- Liczba nowych klientów w aktualnym np miesiącu
- Liczba powracających klientów (klienci, którzy kupili >= 2 razy)
- Średnia liczba zamówień na klienta
- Średnia ocena naszej firmy przez klientów 

### 4.2 Szczegółowe analizy
#### 4.2.1 Segmentacja klientów
Podział klientów na grupy:
- Nowi klienci
- Powracający klienci (ranking najczęściej robionych w firmie zakupów)
- Najlepsi klienci
  - łącznej wartości zakupów,
  - liczby złożonych zamówień,
  - częstotliwości zakupów,
  - średniej wartości zamówienia.
### 4.3 Analiza AI
System automatycznie wykrywa:
- najbardziej wartościowych klientów,
- klientów zagrożonych odejściem,
- wzrost lub spadek liczby nowych klientów,
- zmiany częstotliwości zakupów,
- klientów o największym potencjale sprzedażowym.

# 5. Analiza Allegro Ads
Ocena skuteczności kampanii reklamowych oraz ich wpływu na sprzedaż i zysk.

## 5.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi:
- Łączne wydatki na reklamy
- ROAS
- ACOS
- Liczba kliknięć
- Liczba konwersji

## 5.2 Szczegółowe analizy
- skuteczność kampanii,
- koszt kampanii,
- przychód z reklam,
- ranking kampanii według ROAS,
- ranking kampanii nierentownych.

### Analiza AI
System automatycznie wykrywa:
- kampanie generujące straty,
- kampanie o najwyższej skuteczności,
- rekomendacje zwiększenia lub zmniejszenia budżetu,
- nagłe zmiany efektywności reklam.

# 6. Analiza konkurencji
Monitorowanie działań konkurencji oraz porównanie własnej oferty względem rynku w celu identyfikacji szans zwiększenia sprzedaży i poprawy konkurencyjności.

## 6.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi:
- Średnia cena konkurencji dla porównywanych produktów
- Różnica cen względem konkurencji (%)
- Liczba produktów, dla których konkurencja oferuje lepsze warunki
- Liczba produktów wymagających reakcji

## 6.2 Szczegółowe analizy
### 6.2.1 Porównanie cen
Analiza poziomu cen własnych produktów względem konkurencji:
- porównanie aktualnych cen sprzedaży,
- wykrywanie produktów droższych lub tańszych od konkurencji,
- analiza historii zmian cen,
- wpływ zmian cen na sprzedaż i marżę.

### 6.2.1 Ranking konkurencyjności produktów
Lista produktów według poziomu konkurencyjności:
- produkty bardziej atrakcyjne niż konkurencja,
- produkty wymagające poprawy,
- produkty tracące pozycję na rynku.

### 6.3 Analiza AI
System automatycznie wykrywa:
- produkty, których cena jest niekonkurencyjna,
- konkurentów przejmujących sprzedaż w danej kategorii,
- nagłe zmiany cen konkurencji,
- produkty wymagające optymalizacji oferty,
- możliwości zwiększenia sprzedaży poprzez zmianę ceny, opisu lub promocji.

# 7. Analiza zwrotów i reklamacji
Monitorowanie zwrotów oraz reklamacji klientów w celu identyfikacji problematycznych produktów, ograniczenia strat oraz poprawy jakości obsługi klienta.

## 7.1 Główne wskaźniki
W formie bloczków z aktualnymi danymi:
- Łączna liczba zwrotów
- Współczynnik zwrotów (%)
- Łączna wartość zwróconych zamówień
- Koszt obsługi zwrotów
- Liczba reklamacji

## 7.2 Szczegółowe analizy
### 7.2.1 Analiza zwrotów
Analiza przyczyn i trendów zwrotów:
- liczba zwrotów w czasie,
- produkty z największą liczbą zwrotów,
- produkty z najwyższym współczynnikiem zwrotów,
- wartość utraconej sprzedaży

### 7.2.2 Analiza powodów zwrotów
Klasyfikacja przyczyn zwrotów:
- niezgodność produktu z opisem,
- niewłaściwy rozmiar lub parametry,
- uszkodzenie produktu,
- problem z jakością,
- zmiana decyzji klienta,
- inne przyczyny.

### 7.2.3 Analiza reklamacji
Monitorowanie jakości produktów i obsługi:
- produkty z największą liczbą reklamacji,
- najczęściej zgłaszane problemy

### 7.3 Analiza AI
System automatycznie wykrywa:
- produkty generujące największą liczbę zwrotów,
- produkty o wysokim koszcie obsługi,
- powtarzające się problemy jakościowe,
- wzrost liczby reklamacji,
- negatywne trendy wpływające na ocenę sklepu.

# 8. Prognozy AI
Prognozowanie przyszłych wyników sklepu na podstawie danych historycznych.

## 8.1 Prognozy
System prezentuje prognozy:
- sprzedaży,
- przychodów,
- zysku,
- liczby zamówień,
- wyczerpania zapasów magazynowych.

### Analiza AI
System automatycznie przewiduje:
- prognozowane wyniki sprzedażowe,
- ryzyko braków magazynowych,
- sezonowe wzrosty i spadki sprzedaży,
- produkty wymagające wcześniejszego uzupełnienia zapasów.
  
# 9. Alerty:
Reczy na które trzeba pilnie zwrócić uwagę
Powiadomienia o:
- niskim stanie magazynowym
- spadku sprzedaży,
- wzroście liczby zwrotów,
- spadku marży
