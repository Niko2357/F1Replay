import streamlit as st
import requests
import pandas as pd
from Process.Analysis import Analysis

SESSIONS_API_URL = "https://api.openf1.org/v1/sessions"


@st.cache_data
def fetch_all_sessions(url: str) -> pd.DataFrame:
    """Stáhne a zpracuje seznam všech dostupných relací ze zadaného API."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_data = response.json()

        df = pd.DataFrame(raw_data)

        # Filtrujeme a extrahujeme rok pro UI
        df_filtered = df[df['session_name'] == 'Race'].copy()
        df_filtered['Year'] = pd.to_datetime(df_filtered['date_start']).dt.year.astype(str)

        # Sjednocený název pro dropdown
        df_filtered['Race_Name'] = df_filtered['location'] + " (" + df_filtered['country_name'] + ")"

        return df_filtered[['session_key', 'Year', 'Race_Name', 'location']]

    except Exception as e:
        st.error(f"Nepodařilo se načíst seznam relací OpenF1: {e}")
        return pd.DataFrame()


# --- Streamlit UI ---

st.set_page_config(page_title="F1 Paralelní Analýza Závodů", layout="wide")
st.title("🏎️ F1 Paralelní Analýza Závodů")

# Načtení dat relací
with st.spinner("Načítání seznamu závodů, čekejte prosím..."):
    all_sessions_df = fetch_all_sessions(SESSIONS_API_URL)

if all_sessions_df.empty:
    st.warning("Nelze pokračovat, nepodařilo se načíst data ze sessions API.")
    st.stop()

### Postranní panel s filtry (UI)
with st.sidebar:
    st.header("Filtr Závodu")

    # 1. Výběr Roku
    available_years = sorted(all_sessions_df['Year'].unique(), reverse=True)
    selected_year = st.selectbox("Vyberte Rok:", options=available_years)

    # Filtrování dat podle vybraného roku
    filtered_by_year_df = all_sessions_df[all_sessions_df['Year'] == selected_year]

    # 2. Výběr Závodu
    available_races = sorted(filtered_by_year_df['Race_Name'].unique())
    selected_race_name = st.selectbox("Vyberte Závod:", options=available_races)

    # 3. Získání klíče relace (Session Key)
    final_selection = filtered_by_year_df[
        filtered_by_year_df['Race_Name'] == selected_race_name
        ]

    session_key_to_use = None
    if not final_selection.empty:
        session_key_to_use = str(final_selection['session_key'].iloc[0])
        st.info(f"Klíč relace: **{session_key_to_use}**")

        run_analysis = st.button("Spustit Paralelní Analýzu", type="primary")
    else:
        st.warning("Nelze nalézt data pro vybraný závod.")
        run_analysis = False

# --- Spuštění logiky po stisknutí tlačítka ---
if run_analysis and session_key_to_use:
    st.header(f"Výsledky závodu {selected_race_name} ({selected_year})")

    # Volání vaší upravené paralelní metody s novým klíčem
    with st.spinner(f'Probíhá paralelní analýza výsledků...'):
        results = Analysis.parallel(session_key_to_use)

    if results and not "Error" in results[0]:

        # Zobrazení výsledků v tabulce (splňuje požadavek na UI)
        results_df = pd.DataFrame(results)

        st.dataframe(
            results_df.set_index('Position'),
            use_container_width=True
        )

        # Generování CSV pro stažení (splňuje požadavek na ne-print výstup)
        csv_data = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Stáhnout Výsledky jako CSV",
            data=csv_data,
            file_name=f'{selected_year}_{selected_race_name.replace(" ", "_")}_results.csv',
            mime='text/csv',
        )

        st.success("Analýza dokončena. Data zobrazena a připravena ke stažení.")

    elif results and "Error" in results[0]:
        st.error(f"Analýza se nezdařila: {results[0]['Error']}")
    else:
        st.error("Analýza nevrátila žádné výsledky.")
