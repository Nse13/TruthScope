
import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup

openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

def estrai_testo_da_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragrafi = soup.find_all(['p'])
        testo = " ".join([p.get_text() for p in paragrafi])
        return testo.strip()
    except Exception as e:
        return f"Errore durante l'estrazione del testo: {e}"

def cerca_fonti_online(query, max_results=5):
    try:
        url = "https://serpapi.com/search"
        params = {"q": query, "api_key": SERPAPI_KEY, "engine": "google", "num": max_results}
        response = requests.get(url, params=params)
        risultati = response.json()
        link_fonti = []
        for item in risultati.get("organic_results", []):
            titolo = item.get("title")
            link = item.get("link")
            snippet = item.get("snippet", "")
            if titolo and link:
                link_fonti.append(f"{titolo} - {snippet} ({link})")
        return link_fonti
    except Exception as e:
        return [f"Errore nella ricerca fonti: {e}"]
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def valuta_veridicita_e_accuratezza(testo, fonti):
    prompt = f"""
Testo da verificare:
{testo}

Fonti esterne trovate:
{chr(10).join(fonti)}

Compito:
1. Valuta se il contenuto è Verificato, Parzialmente vero, Falso o Non verificabile.
2. Dai un punteggio di accuratezza da 0 a 100 basato sul confronto con le fonti.
3. Fornisci una spiegazione chiara e sintetica.

Risultato:
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un esperto di fact-checking e analisi di accuratezza."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()




# INTERFACCIA STREAMLIT
st.title("🔎 TruthScope – Analisi Veridicità Articoli e Post")
url = st.text_input("Incolla qui il link all'articolo o post da analizzare")

if st.button("Analizza"):
    if not url.strip():
        st.warning("Inserisci un URL valido.")
    else:
        with st.spinner("Estrazione e analisi in corso..."):
            testo = estrai_testo_da_url(url)
            if testo.startswith("Errore"):
                st.error(testo)
            else:
                fonti = cerca_fonti_online(testo[:200])
                valutazione = valuta_veridicita_e_accuratezza(testo[:3000], fonti)
                st.success("Analisi completata!")
                st.subheader("📝 Testo analizzato:")
                st.write(testo[:1000] + "..." if len(testo) > 1000 else testo)
                st.subheader("🌐 Fonti trovate online:")
                for fonte in fonti:
                    st.markdown(f"- {fonte}")
                st.subheader("📊 Valutazione AI:")
                st.info(valutazione)
