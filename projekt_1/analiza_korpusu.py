import os
import re
from collections import Counter, defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import nltk
import networkx as nx
from typing import List, Dict, Tuple

# Pobierz zasoby NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)


class AnalizaKorpusu:
    def __init__(self, sciezka_korpusu: str):
        self.sciezka_korpusu = sciezka_korpusu
        self.slowa = []
        self.df_analiza = None
        self.graf_sasiedztwa = None
        
    def wczytaj_korpus(self, limit_slow=100000) -> None:
        print(f"Wczytywanie korpusu z: {self.sciezka_korpusu}")
        
        with open(self.sciezka_korpusu, 'r', encoding='utf-8') as f:
            tekst = f.read()
        
        slowa_raw = re.findall(r'\b[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+\b', tekst.lower())
        
        slowa_filtrowane = [
            slowo for slowo in slowa_raw 
            if len(slowo) > 1 or slowo in ['i', 'a']
        ]
        
        self.slowa = slowa_filtrowane[:limit_slow]
        
        print(f"Wczytano {len(self.slowa):,} słów")
        
    def oblicz_statystyki(self) -> pd.DataFrame:
        print("\nObliczanie statystyk...")
        
        licznik = Counter(self.slowa)
        posortowane = licznik.most_common()
        
        dane = []
        for ranga, (wyraz, czestotliwosc) in enumerate(posortowane, start=1):
            dane.append({
                'wyraz': wyraz,
                'r': ranga,
                'f': czestotliwosc,
                'r*f': ranga * czestotliwosc
            })
        
        self.df_analiza = pd.DataFrame(dane)
        
        print(f"Znaleziono {len(self.df_analiza)} unikalnych wyrazów")
        
        return self.df_analiza
    
    def pokaz_tabele(self, n=20) -> None:
        print(f"\nTabela częstotliwości (top {n}):")
        print("=" * 70)
        print(self.df_analiza.head(n).to_string(index=False))
        print("=" * 70)
        
    def wykres_zipfa(self, zapisz=True) -> None:
        print("\nGenerowanie wykresu prawa Zipfa...")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(self.df_analiza['r'], self.df_analiza['f'], 'b-', linewidth=1.5, alpha=0.7)
        ax1.set_xlabel('Ranga (r)', fontsize=12)
        ax1.set_ylabel('Częstotliwość (f)', fontsize=12)
        ax1.set_title('Prawo Zipfa - Skala Liniowa', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        ax2.loglog(self.df_analiza['r'], self.df_analiza['f'], 'r-', linewidth=1.5, alpha=0.7)
        ax2.set_xlabel('Ranga (r) - skala log', fontsize=12)
        ax2.set_ylabel('Częstotliwość (f) - skala log', fontsize=12)
        ax2.set_title('Prawo Zipfa - Skala Logarytmiczna', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        
        if zapisz:
            sciezka = os.path.join(os.path.dirname(self.sciezka_korpusu), '..', 'wykres_zipfa.png')
            plt.savefig(sciezka, dpi=300, bbox_inches='tight')
            print(f"Wykres zapisany: {sciezka}")
        
        plt.show()
        
    def odciecie_90_procent(self) -> Tuple[int, pd.DataFrame]:
        print("\nObliczanie odcięcia 90%...")
        
        suma_calkowita = self.df_analiza['f'].sum()
        prog_90 = 0.9 * suma_calkowita
        
        suma_kumulatywna = 0
        pozycja_odciecia = 0
        
        for idx, row in self.df_analiza.iterrows():
            suma_kumulatywna += row['f']
            if suma_kumulatywna >= prog_90:
                pozycja_odciecia = idx + 1
                break
        
        df_90 = self.df_analiza.iloc[:pozycja_odciecia]
        
        print(f"90% wystąpień pokrywa {pozycja_odciecia} najczęstszych słów")
        print(f"(z {len(self.df_analiza)} unikalnych słów)")
        print(f"Procent unikalnych słów: {100*pozycja_odciecia/len(self.df_analiza):.2f}%")
        
        return pozycja_odciecia, df_90
    
    def generuj_graf_sasiedztwa(self, min_czestotliwosc=5) -> nx.Graph:
        print("\nGenerowanie grafu sąsiedztwa słów...")
        
        with open(self.sciezka_korpusu, 'r', encoding='utf-8') as f:
            tekst = f.read()
        
        zdania = re.split(r'[.!?]+', tekst)
        pary = defaultdict(int)
        
        for zdanie in zdania:
            zdanie_clean = re.sub(r'[^\w\s]', ' ', zdanie.lower())
            slowa_zdania = zdanie_clean.split()
            
            for i in range(len(slowa_zdania) - 1):
                slowo1 = slowa_zdania[i]
                slowo2 = slowa_zdania[i + 1]
                
                if slowo1 and slowo2 and len(slowo1) > 1 and len(slowo2) > 1:
                    para = tuple(sorted([slowo1, slowo2]))
                    pary[para] += 1
        
        G = nx.Graph()
        
        for (slowo1, slowo2), waga in pary.items():
            if waga >= min_czestotliwosc:
                G.add_edge(slowo1, slowo2, weight=waga)
        
        self.graf_sasiedztwa = G
        
        print(f"Graf utworzony:")
        print(f"Węzły (słowa): {G.number_of_nodes()}")
        print(f"Krawędzie (połączenia): {G.number_of_edges()}")
        
        return G
    
    def wizualizuj_graf(self, top_n=50, zapisz=True) -> None:
        print(f"\nWizualizacja grafu (top {top_n} najbardziej połączonych słów)...")
        
        if self.graf_sasiedztwa is None:
            print("Najpierw wygeneruj graf używając generuj_graf_sasiedztwa()")
            return
        
        stopnie = dict(self.graf_sasiedztwa.degree())
        top_wezly = sorted(stopnie.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_nazwy = [w[0] for w in top_wezly]
        
        podgraf = self.graf_sasiedztwa.subgraph(top_nazwy)
        
        plt.figure(figsize=(16, 12))
        
        pos = nx.spring_layout(podgraf, k=0.5, iterations=50, seed=42)
        
        rozmiary = [stopnie[node] * 30 for node in podgraf.nodes()]
        
        nx.draw_networkx_nodes(podgraf, pos, node_size=rozmiary, 
                               node_color='lightblue', alpha=0.7, 
                               edgecolors='navy', linewidths=1.5)
        
        nx.draw_networkx_edges(podgraf, pos, alpha=0.3, width=0.5)
        
        nx.draw_networkx_labels(podgraf, pos, font_size=8, font_weight='bold')
        
        plt.title(f'Graf Sąsiedztwa Słów (Top {top_n})', fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        if zapisz:
            sciezka = os.path.join(os.path.dirname(self.sciezka_korpusu), '..', 'graf_sasiedztwa.png')
            plt.savefig(sciezka, dpi=300, bbox_inches='tight')
            print(f"Graf zapisany: {sciezka}")
        
        plt.show()
    
    def znajdz_rzeczowniki(self, top_n=50) -> pd.DataFrame:
        print(f"\nIdentyfikacja top {top_n} rzeczowników...")
        
        rzeczowniki = []
        unikalne_slowa = self.df_analiza['wyraz'].tolist()
        
        batch_size = 1000
        wszystkie_tagi = []
        
        for i in range(0, len(unikalne_slowa), batch_size):
            batch = unikalne_slowa[i:i+batch_size]
            tagi = nltk.pos_tag(batch)
            wszystkie_tagi.extend(tagi)
        
        slownik_tagow = dict(wszystkie_tagi)
        
        for idx, row in self.df_analiza.iterrows():
            wyraz = row['wyraz']
            tag = slownik_tagow.get(wyraz, '')
            
            if tag.startswith('NN'):
                rzeczowniki.append(row)
            
            if len(rzeczowniki) >= top_n:
                break
        
        df_rzeczowniki = pd.DataFrame(rzeczowniki)
        
        print(f"Znaleziono {len(df_rzeczowniki)} rzeczowników")
        print(f"\nTop {min(top_n, len(df_rzeczowniki))} rzeczowników:")
        print("=" * 70)
        print(df_rzeczowniki.head(top_n).to_string(index=False))
        print("=" * 70)
        
        return df_rzeczowniki
    
    def zapisz_wyniki(self) -> None:
        print("\nZapisywanie wyników...")
        
        katalog = os.path.dirname(self.sciezka_korpusu)
        katalog_projekt = os.path.join(katalog, '..')
        
        sciezka_csv = os.path.join(katalog_projekt, 'analiza_czestotliwosci.csv')
        self.df_analiza.to_csv(sciezka_csv, index=False, encoding='utf-8')
        print(f"Tabela zapisana: {sciezka_csv}")


def main():
    print("=" * 70)
    print("  ANALIZA KORPUSU JĘZYKOWEGO - PROJEKT 1")
    print("=" * 70)
    
    # Ścieżka do korpusu
    sciezka_korpusu = os.path.join(
        os.path.dirname(__file__), 
        'corpus', 
        'corpus.txt'
    )
    
    analiza = AnalizaKorpusu(sciezka_korpusu)
    
    analiza.wczytaj_korpus(limit_slow=100000)
    df = analiza.oblicz_statystyki()
    analiza.pokaz_tabele(n=30)
    analiza.wykres_zipfa()
    pozycja, df_90 = analiza.odciecie_90_procent()
    graf = analiza.generuj_graf_sasiedztwa(min_czestotliwosc=3)
    analiza.wizualizuj_graf(top_n=50)
    df_rzeczowniki = analiza.znajdz_rzeczowniki(top_n=50)
    analiza.zapisz_wyniki()
    
    print("\n" + "=" * 70)
    print("  ANALIZA ZAKOŃCZONA POMYŚLNIE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
