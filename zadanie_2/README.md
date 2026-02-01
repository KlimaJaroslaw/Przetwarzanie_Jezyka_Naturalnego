# 🤖 Generator Zdań SVO - Projekt NLP

Projekt edukacyjny z zakresu przetwarzania języka naturalnego (NLP). Aplikacja pozwala na interaktywne budowanie poprawnych gramatycznie zdań w języku angielskim według struktury **SVO (Subject - Verb - Object)**. Program prowadzi użytkownika krok po kroku, dbając o zgodność osoby, liczby oraz czasu.

## 📋 Funkcje aplikacji
- **Prowadzenie za rękę (Step-by-step):** Interfejs podzielony na 3 etapy (Podmiot, Czasownik, Dopełnienie).
- **Logika gramatyczna:**
  - Automatyczna odmiana czasowników przez osoby (np. *eat* -> *eats* w 3. os. l.poj.).
  - Obsługa czasów: Present Simple, Past Simple (czasowniki nieregularne), Future Simple.
  - Tworzenie przeczeń i pytań z odpowiednimi operatorami (*do/does/did/will*).
  - Automatyczny dobór przedimków (*a/an*) na podstawie brzmienia następnego słowa.
  - Obsługa liczby mnogiej rzeczowników.
- **Baza słownikowa:** Wybór spośród 100 rzeczowników, 100 czasowników i 100 przymiotników.

## 🛠️ Technologie
- **Python** (Język główny)
- **Streamlit** (Interfejs graficzny w przeglądarce)
- **inflect** (Logika liczby mnogiej i przedimków)
- **lemminflect** (Logika odmiany czasowników)

## 🚀 Instalacja i uruchomienie

### 1. Klonowanie/Przygotowanie plików
Upewnij się, że w folderze projektu znajdują się następujące pliki:
- `app.py` (kod aplikacji)
- `data.json` (baza słów)
- `requirements.txt` (lista bibliotek)

### 2. Instalacja bibliotek
Otwórz terminal w folderze projektu i wpisz:
```bash
pip install -r requirements.txt