# Projekt 1 - Analiza Korpusu Językowego

## Opis
Program analizuje korpus 100,000 wyrazów i wykonuje kompleksową analizę lingwistyczną.

## Funkcjonalności

1. **Analiza częstotliwości** - Tabela: wyraz | r (ranga) | f (częstotliwość) | r*f
2. **Prawo Zipfa** - Wizualizacja rozkładu częstotliwości
3. **Odcięcie 90%** - Identyfikacja minimalnego zestawu słów pokrywających 90% tekstu
4. **Graf sąsiedztwa** - Wizualizacja relacji między sąsiednimi słowami
5. **Top 50 rzeczowników** - Ranking najczęstszych rzeczowników

## Instalacja

### 1. Utwórz środowisko wirtualne

```bash
python -m venv venv
```

### 2. Aktywuj środowisko

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

## Użycie

Uruchom program:

```bash
python analiza_korpusu.py
```

## Wyniki

Program generuje:
- `analiza_czestotliwosci.csv` - Pełna tabela częstotliwości
- `wykres_zipfa.png` - Wizualizacja prawa Zipfa
- `graf_sasiedztwa.png` - Graf powiązań między słowami
- Wydruk top 50 rzeczowników w konsoli

## Wymagania

- Python 3.8+
- matplotlib
- pandas
- numpy
- nltk
- networkx

## Struktura projektu

```
projekt_1/
├── corpus/
│   └── corpus.txt           # Korpus 100k słów
├── analiza_korpusu.py       # Główny program
├── requirements.txt         # Zależności
├── README.md               # Dokumentacja
├── wykres_zipfa.png        # Wynik (generowany)
├── graf_sasiedztwa.png     # Wynik (generowany)
└── analiza_czestotliwosci.csv  # Wynik (generowany)
```

## Informacje projektowe

Projekt wykonany w ramach zajęć z Przetwarzania Języka Naturalnego (PJN)
Jarosław Klima
Paweł Knot
