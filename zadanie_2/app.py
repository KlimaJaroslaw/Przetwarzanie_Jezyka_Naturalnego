import streamlit as st
import json

with open('data.json','r',encoding='utf-8') as f:
    data = json.load(f)

nouns = data['nouns']
adjectives = data['adjectives']
verbs = data['verbs']

# ------- OGÓLNE USTAWIENIA STRONY --------
st.set_page_config(page_title="Budowniczy Zdań SVO", layout="centered")
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'sentence_data' not in st.session_state:
    st.session_state.sentence_data = {}
st.title("Kreator Zdań SVO")
st.write("Program pomoże Ci zbudować poprawne zdanie krok po kroku.")



# ------- WYBÓR PODMIOTU ------------
if st.session_state.step == 1:
    st.header("Krok 1: Wybierz Podmiot (Subject)")
    
    col1, col2 = st.columns(2)
    with col1:
        noun = st.selectbox("Wybierz rzeczownik:", nouns)
        number = st.radio("Liczba:", ["pojedyncza", "mnoga"])
    
    with col2:
        has_adj = st.checkbox("Czy dodać przymiotnik?")
        adj = st.selectbox("Wybierz przymiotnik:", adjectives) if has_adj else None

    person = st.select_slider("Osoba:", options=[1, 2, 3], value=3)

    if st.button("Dalej"):
        st.session_state.sentence_data['subject'] = {
            'noun': noun, 'number': number, 'adj': adj, 'person': person
        }
        st.session_state.step = 2
        st.rerun()




# -------- WYBÓR CZASOWNIKA ----------
elif st.session_state.step == 2:
    st.header("Krok 2: Wybierz Czasownik (Verb)")
    
    verb = st.selectbox("Wybierz czasownik:", verbs)
    tense = st.selectbox("Czas:", ["Present Simple", "Past Simple", "Future Simple"])
    type_ = st.radio("Typ zdania:", ["twierdzące", "przeczące", "pytające"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Powrót"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Dalej"):
            st.session_state.sentence_data['verb'] = {
                'base': verb, 'tense': tense, 'type': type_
            }
            st.session_state.step = 3
            st.rerun()



# -------- WYBÓR DOPEŁNIENIA ----------
elif st.session_state.step == 3:
    st.header("Krok 3: Wybierz Dopełnienie (Object)")
    
    obj_noun = st.selectbox("Co jest obiektem?", nouns)
    article = st.radio("Przedimek:", ["a/an", "the", "brak"])

    if st.button("Powrót"):
        st.session_state.step = 2
        st.rerun()
    
    if st.button("Generuj zdanie!"):
        st.session_state.sentence_data['object'] = {'noun': obj_noun, 'article': article}
        st.session_state.step = 4
        st.rerun()



# ---------- WYGENEROWANE ZDANIE -------------
elif st.session_state.step == 4:
    st.header("Twoje wygenerowane zdanie:")
    
    data = st.session_state.sentence_data
    s = f"{data['subject']['adj'] or ''} {data['subject']['noun']}"
    v = data['verb']['base']
    o = f"{data['object']['article'] if data['object']['article'] != 'brak' else ''} {data['object']['noun']}"
    
    full_sentence = f"{s} {v} {o}.".capitalize()
    
    st.success(full_sentence)
    
    if st.button("Zacznij od nowa"):
        st.session_state.step = 1
        st.session_state.sentence_data = {}
        st.rerun()