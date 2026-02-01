import streamlit as st
import json
import inflect
from lemminflect import getInflection

p = inflect.engine()

def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Nie znaleziono pliku data.json! Upewnij się, że jest w tym samym folderze.")
        return {"nouns": [], "adjectives": [], "verbs": []}

def build_sentence(data):
    s = data['subject']
    v = data['verb']
    o = data['object']
    
    subj_noun = p.plural(s['noun']) if s['number'] == "mnoga" else s['noun']
    subj_phrase = f"{s['adj']} {subj_noun}" if s['adj'] else subj_noun
    if s['number'] == "pojedyncza":
        subj_final = p.a(subj_phrase)
    else:
        subj_final = subj_phrase
    
    v_base = v['base']
    tense = v['tense']
    mode = v['type'] 
    
    is_3rd_singular = (s['person'] == 3 and s['number'] == "pojedyncza")
    
    result = ""
    
    if mode == "rozkazujące":
        return f"{v_base} {o['noun']}!".capitalize()

    if tense == "Present Simple":
        if mode == "twierdzące":
            v_form = getInflection(v_base, tag='VBZ' if is_3rd_singular else 'VBP')[0]
            result = f"{subj_final} {v_form}"
        elif mode == "przeczące":
            aux = "doesn't" if is_3rd_singular else "don't"
            result = f"{subj_final} {aux} {v_base}"
        elif mode == "pytające":
            aux = "Does" if is_3rd_singular else "Do"
            result = f"{aux} {subj_final} {v_base}"

    elif tense == "Past Simple":
        v_past = getInflection(v_base, tag='VBD')[0]
        if mode == "twierdzące":
            result = f"{subj_final} {v_past}"
        elif mode == "przeczące":
            result = f"{subj_final} didn't {v_base}"
        elif mode == "pytające":
            result = f"Did {subj_final} {v_base}"

    elif tense == "Future Simple":
        if mode == "twierdzące":
            result = f"{subj_final} will {v_base}"
        elif mode == "przeczące":
            result = f"{subj_final} won't {v_base}"
        elif mode == "pytające":
            result = f"Will {subj_final} {v_base}"

    obj_noun = o['noun']
    if o['article'] == "a/an":
        obj_final = p.a(obj_noun)
    elif o['article'] == "the":
        obj_final = f"the {obj_noun}"
    else:
        obj_final = obj_noun

    punctuation = "?" if mode == "pytające" else "."
    final_sentence = f"{result} {obj_final}{punctuation}"
    return final_sentence.capitalize()

st.set_page_config(page_title="Grammar Builder", page_icon="✍️")
data = load_data()

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'sentence_data' not in st.session_state:
    st.session_state.sentence_data = {}

st.title("🤖 Generator Poprawnej Gramatyki (SVO)")

steps = ["Podmiot", "Czasownik", "Dopełnienie", "Wynik"]
st.progress(st.session_state.step / 4)

if st.session_state.step == 1:
    st.subheader("Krok 1: Zdefiniuj Podmiot (S)")
    with st.expander("Wybierz cechy podmiotu", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            number = st.radio("Liczba:", ["pojedyncza", "mnoga"])
            person = st.select_slider("Osoba:", options=[1, 2, 3], value=3)
        with col2:
            noun = st.selectbox("Wybierz rzeczownik:", data['nouns'])
            use_adj = st.checkbox("Dodać przymiotnik?")
            adj = st.selectbox("Wybierz przymiotnik:", data['adjectives']) if use_adj else None

    if st.button("Dalej ➡️"):
        st.session_state.sentence_data['subject'] = {
            'noun': noun, 'number': number, 'person': person, 'adj': adj
        }
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("Krok 2: Zdefiniuj Czasownik (V)")
    verb = st.selectbox("Wybierz czasownik podstawowy:", data['verbs'])
    
    col1, col2 = st.columns(2)
    with col1:
        tense = st.selectbox("Wybierz czas:", ["Present Simple", "Past Simple", "Future Simple"])
    with col2:
        mode = st.radio("Rodzaj zdania:", ["twierdzące", "przeczące", "pytające", "rozkazujące"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Powrót"):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.button("Dalej ➡️"):
            st.session_state.sentence_data['verb'] = {
                'base': verb, 'tense': tense, 'type': mode
            }
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.subheader("Krok 3: Zdefiniuj Dopełnienie (O)")
    obj_noun = st.selectbox("Wybierz rzeczownik (obiekt):", data['nouns'])
    article = st.radio("Przedimek:", ["a/an", "the", "brak"])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Powrót"):
            st.session_state.step = 2
            st.rerun()
    with c2:
        if st.button("Generuj Zdanie 🚀"):
            st.session_state.sentence_data['object'] = {
                'noun': obj_noun, 'article': article
            }
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.subheader("Twój wynik:")
    
    sentence = build_sentence(st.session_state.sentence_data)
    
    st.info("Wygenerowane poprawne zdanie:")
    st.header(f"\"{sentence}\"")
    
    st.divider()
    if st.button("Zacznij od nowa 🔄"):
        st.session_state.step = 1
        st.session_state.sentence_data = {}
        st.rerun()