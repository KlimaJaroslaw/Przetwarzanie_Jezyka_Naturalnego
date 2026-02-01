# Projekt 3 - Analiza Semantyczna

## Opis
Program analizuje korpus 100,000 wyrazów i tworzy grafy dwudzielne pokazujące relacje semantyczne między różnymi częściami mowy.

## Funkcjonalności

1. **Analiza części mowy (POS)** - Identyfikacja rzeczowników, przymiotników i czasowników używając spaCy
2. **Grafy dwudzielne**:
   - Przymiotnik-Rzeczownik (100 przymiotników × 100 rzeczowników)
   - Czasownik-Rzeczownik (100 czasowników × 100 rzeczowników)
3. **System kolorowania**:
   - Czerwony: 0 wystąpień
   - Żółty: 1 wystąpienie
   - Zielony: 2-10 wystąpień
   - Niebieski: >10 wystąpień
4. **Listy połączeń** - Szczegółowe listy dla każdego przymiotnika/czasownika
5. **Macierze połączeń** - Wizualizacja heatmap

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
python -m spacy download en_core_web_sm
```

## Użycie

```bash
python analiza_semantyczna.py
```

## Wyniki

Program generuje:
- `graf_przymiotnik_rzeczownik.png` - Graf dwudzielny ADJ-NOUN
- `graf_czasownik_rzeczownik.png` - Graf dwudzielny VERB-NOUN
- `macierz_przymiotnik_rzeczownik.png` - Heatmap ADJ-NOUN
- `macierz_czasownik_rzeczownik.png` - Heatmap VERB-NOUN
- `lista_przymiotnik_rzeczownik.txt` - Szczegółowa lista połączeń
- `lista_czasownik_rzeczownik.txt` - Szczegółowa lista połączeń

## Wymagania

- Python 3.8+
- spacy (z modelem en_core_web_sm)
- matplotlib
- pandas
- numpy
- networkx

## Struktura projektu

```
projekt_3/
├── corpus/
│   └── corpus.txt              # Korpus 100k słów
├── analiza_semantyczna.py      # Główny program
├── requirements.txt            # Zależności
├── README.md                  # Dokumentacja
└── venv/                      # Środowisko wirtualne
```
