import os
import re
from collections import defaultdict, Counter
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite
import spacy
from typing import Dict, List, Tuple, Set

plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'


class AnalizaSemanyczna:
    
    def __init__(self, sciezka_korpusu: str):
        self.sciezka_korpusu = sciezka_korpusu
        self.nlp = None
        self.rzeczowniki = []
        self.przymiotniki = []
        self.czasowniki = []
        self.polaczenia_adj_noun = defaultdict(lambda: defaultdict(int))
        self.polaczenia_verb_noun = defaultdict(lambda: defaultdict(int))
        
    def zaladuj_spacy(self):
        print("Ładowanie modelu spaCy...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Model en_core_web_sm nie znaleziony.")
            print("Instalacja modelu...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        print("Model załadowany.\n")
        
    def wczytaj_korpus(self, limit_slow=100000):
        print(f"Wczytywanie korpusu z: {self.sciezka_korpusu}")
        
        with open(self.sciezka_korpusu, 'r', encoding='utf-8') as f:
            tekst = f.read()
        
        slowa_raw = re.findall(r'\b[a-zA-Z]+\b', tekst.lower())
        slowa = slowa_raw[:limit_slow]
        
        print(f"Wczytano {len(slowa):,} słów\n")
        return ' '.join(slowa)
        
    def analiza_pos(self, tekst: str):
        print("Analiza części mowy (POS tagging)...")
        
        doc = self.nlp(tekst)
        
        rzeczowniki_counter = Counter()
        przymiotniki_counter = Counter()
        czasowniki_counter = Counter()
        
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 2:
                rzeczowniki_counter[token.text] += 1
            elif token.pos_ == "ADJ" and len(token.text) > 2:
                przymiotniki_counter[token.text] += 1
            elif token.pos_ == "VERB" and len(token.text) > 2:
                czasowniki_counter[token.text] += 1
        
        self.rzeczowniki = [word for word, _ in rzeczowniki_counter.most_common(100)]
        self.przymiotniki = [word for word, _ in przymiotniki_counter.most_common(100)]
        self.czasowniki = [word for word, _ in czasowniki_counter.most_common(100)]
        
        print(f"Znaleziono {len(self.rzeczowniki)} top rzeczowników")
        print(f"Znaleziono {len(self.przymiotniki)} top przymiotników")
        print(f"Znaleziono {len(self.czasowniki)} top czasowników\n")
        
    def znajdz_polaczenia(self, tekst: str):
        print("Szukanie połączeń przymiotnik-rzeczownik i czasownik-rzeczownik...")
        
        doc = self.nlp(tekst)
        
        rzeczowniki_set = set(self.rzeczowniki)
        przymiotniki_set = set(self.przymiotniki)
        czasowniki_set = set(self.czasowniki)
        
        for i, token in enumerate(doc):
            if token.text in rzeczowniki_set:
                if i > 0 and doc[i-1].text in przymiotniki_set:
                    self.polaczenia_adj_noun[doc[i-1].text][token.text] += 1
                
                if i > 0 and doc[i-1].text in czasowniki_set:
                    self.polaczenia_verb_noun[doc[i-1].text][token.text] += 1
                    
                if i < len(doc) - 1 and doc[i+1].text in czasowniki_set:
                    self.polaczenia_verb_noun[doc[i+1].text][token.text] += 1
        
        print(f"Znaleziono {sum(len(v) for v in self.polaczenia_adj_noun.values())} połączeń przymiotnik-rzeczownik")
        print(f"Znaleziono {sum(len(v) for v in self.polaczenia_verb_noun.values())} połączeń czasownik-rzeczownik\n")
        
    def get_color(self, count: int) -> str:
        if count == 0:
            return '#e74c3c'
        elif count == 1:
            return '#f39c12'
        elif count <= 10:
            return '#27ae60'
        else:
            return '#3498db'
            
    def wizualizuj_graf_dwudzielny(self, typ='adj-noun', top_n=30, zapisz=True):
        if typ == 'adj-noun':
            polaczenia = self.polaczenia_adj_noun
            set_a = self.przymiotniki[:top_n]
            set_b = self.rzeczowniki[:top_n]
            tytul = f'Graf Dwudzielny: Przymiotnik-Rzeczownik (Top {top_n})'
            nazwa_pliku = 'graf_przymiotnik_rzeczownik.png'
            label_a = 'Przymiotniki'
            label_b = 'Rzeczowniki'
        else:
            polaczenia = self.polaczenia_verb_noun
            set_a = self.czasowniki[:top_n]
            set_b = self.rzeczowniki[:top_n]
            tytul = f'Graf Dwudzielny: Czasownik-Rzeczownik (Top {top_n})'
            nazwa_pliku = 'graf_czasownik_rzeczownik.png'
            label_a = 'Czasowniki'
            label_b = 'Rzeczowniki'
            
        print(f"Wizualizacja: {tytul}")
        
        G = nx.Graph()
        
        for node in set_a:
            G.add_node(node, bipartite=0)
        for node in set_b:
            G.add_node(node, bipartite=1)
        
        edge_colors = []
        edge_widths = []
        
        for word_a in set_a:
            if word_a in polaczenia:
                for word_b in set_b:
                    count = polaczenia[word_a].get(word_b, 0)
                    if count > 0:
                        G.add_edge(word_a, word_b, weight=count)
                        edge_colors.append(self.get_color(count))
                        edge_widths.append(min(count * 0.5, 5))
        
        fig, ax = plt.subplots(figsize=(18, 12))
        
        pos = {}
        y_spacing_a = 1.0 / (len(set_a) + 1)
        y_spacing_b = 1.0 / (len(set_b) + 1)
        
        for i, node in enumerate(set_a):
            pos[node] = (0, 1 - (i + 1) * y_spacing_a)
        for i, node in enumerate(set_b):
            pos[node] = (1, 1 - (i + 1) * y_spacing_b)
        
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, alpha=0.6, ax=ax)
        
        nx.draw_networkx_nodes(G, pos, nodelist=set_a, node_color='#ecf0f1', 
                               node_size=800, node_shape='s', edgecolors='#34495e', 
                               linewidths=2, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=set_b, node_color='#ecf0f1', 
                               node_size=800, node_shape='o', edgecolors='#34495e', 
                               linewidths=2, ax=ax)
        
        labels_a = {node: node for node in set_a}
        labels_b = {node: node for node in set_b}
        
        nx.draw_networkx_labels(G, pos, labels_a, font_size=8, font_weight='bold', ax=ax)
        nx.draw_networkx_labels(G, pos, labels_b, font_size=8, font_weight='bold', ax=ax)
        
        ax.text(0, 1.05, label_a, ha='center', fontsize=14, fontweight='bold')
        ax.text(1, 1.05, label_b, ha='center', fontsize=14, fontweight='bold')
        
        legend_elements = [
            mpatches.Patch(facecolor='#e74c3c', label='0 wystąpień'),
            mpatches.Patch(facecolor='#f39c12', label='1 wystąpienie'),
            mpatches.Patch(facecolor='#27ae60', label='2-10 wystąpień'),
            mpatches.Patch(facecolor='#3498db', label='>10 wystąpień')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  ncol=4, frameon=True, fontsize=10)
        
        ax.set_title(tytul, fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        if zapisz:
            sciezka = os.path.join(os.path.dirname(self.sciezka_korpusu), '..', nazwa_pliku)
            plt.savefig(sciezka, dpi=300, bbox_inches='tight')
            print(f"Graf zapisany: {sciezka}")
        
        plt.show()
        
    def generuj_listy_polaczen(self):
        print("\nGenerowanie list połączeń...")
        
        katalog = os.path.dirname(self.sciezka_korpusu)
        katalog_projekt = os.path.join(katalog, '..')
        
        with open(os.path.join(katalog_projekt, 'lista_przymiotnik_rzeczownik.txt'), 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LISTA POŁĄCZEŃ: PRZYMIOTNIK -> RZECZOWNIKI\n")
            f.write("=" * 80 + "\n\n")
            
            for adj in self.przymiotniki:
                if adj in self.polaczenia_adj_noun:
                    rzeczowniki_sorted = sorted(
                        self.polaczenia_adj_noun[adj].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    f.write(f"\n{adj.upper()}:\n")
                    f.write("-" * 60 + "\n")
                    
                    for noun, count in rzeczowniki_sorted:
                        f.write(f"  {noun:<20} [{count:>3} wystąpień]\n")
        
        with open(os.path.join(katalog_projekt, 'lista_czasownik_rzeczownik.txt'), 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LISTA POŁĄCZEŃ: CZASOWNIK -> RZECZOWNIKI\n")
            f.write("=" * 80 + "\n\n")
            
            for verb in self.czasowniki:
                if verb in self.polaczenia_verb_noun:
                    rzeczowniki_sorted = sorted(
                        self.polaczenia_verb_noun[verb].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    f.write(f"\n{verb.upper()}:\n")
                    f.write("-" * 60 + "\n")
                    
                    for noun, count in rzeczowniki_sorted:
                        f.write(f"  {noun:<20} [{count:>3} wystąpień]\n")
        
        print("Listy zapisane:")
        print(f"  - lista_przymiotnik_rzeczownik.txt")
        print(f"  - lista_czasownik_rzeczownik.txt")
        
    def generuj_macierz_polaczen(self, typ='adj-noun'):
        if typ == 'adj-noun':
            polaczenia = self.polaczenia_adj_noun
            set_a = self.przymiotniki[:50]
            set_b = self.rzeczowniki[:50]
            tytul = 'Macierz Połączeń: Przymiotnik-Rzeczownik'
            nazwa_pliku = 'macierz_przymiotnik_rzeczownik.png'
        else:
            polaczenia = self.polaczenia_verb_noun
            set_a = self.czasowniki[:50]
            set_b = self.rzeczowniki[:50]
            tytul = 'Macierz Połączeń: Czasownik-Rzeczownik'
            nazwa_pliku = 'macierz_czasownik_rzeczownik.png'
        
        print(f"\nGenerowanie macierzy: {tytul}")
        
        matrix = np.zeros((len(set_a), len(set_b)))
        
        for i, word_a in enumerate(set_a):
            if word_a in polaczenia:
                for j, word_b in enumerate(set_b):
                    matrix[i, j] = polaczenia[word_a].get(word_b, 0)
        
        fig, ax = plt.subplots(figsize=(16, 14))
        
        colors_map = []
        for val in matrix.flatten():
            colors_map.append(self.get_color(val))
        
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', interpolation='nearest')
        
        ax.set_xticks(np.arange(len(set_b)))
        ax.set_yticks(np.arange(len(set_a)))
        ax.set_xticklabels(set_b, rotation=90, ha='right', fontsize=7)
        ax.set_yticklabels(set_a, fontsize=7)
        
        ax.set_title(tytul, fontsize=16, fontweight='bold', pad=20)
        
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Liczba wystąpień', rotation=270, labelpad=20, fontsize=12)
        
        plt.tight_layout()
        
        sciezka = os.path.join(os.path.dirname(self.sciezka_korpusu), '..', nazwa_pliku)
        plt.savefig(sciezka, dpi=300, bbox_inches='tight')
        print(f"Macierz zapisana: {sciezka}")
        
        plt.show()


def main():
    print("=" * 80)
    print("  PROJEKT 3: ANALIZA SEMANTYCZNA")
    print("  Grafy dwudzielne: Przymiotnik-Rzeczownik i Czasownik-Rzeczownik")
    print("=" * 80 + "\n")
    
    sciezka_korpusu = os.path.join(
        os.path.dirname(__file__),
        'corpus',
        'corpus.txt'
    )
    
    analiza = AnalizaSemanyczna(sciezka_korpusu)
    
    analiza.zaladuj_spacy()
    
    tekst = analiza.wczytaj_korpus(limit_slow=100000)
    
    analiza.analiza_pos(tekst)
    
    analiza.znajdz_polaczenia(tekst)
    
    analiza.wizualizuj_graf_dwudzielny(typ='adj-noun', top_n=30)
    
    analiza.wizualizuj_graf_dwudzielny(typ='verb-noun', top_n=30)
    
    analiza.generuj_macierz_polaczen(typ='adj-noun')
    
    analiza.generuj_macierz_polaczen(typ='verb-noun')
    
    analiza.generuj_listy_polaczen()
    
    print("\n" + "=" * 80)
    print("  ANALIZA ZAKOŃCZONA POMYŚLNIE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
