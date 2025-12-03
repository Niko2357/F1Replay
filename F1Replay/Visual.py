import streamlit as st
import requests
import pandas as pd
from Process.Analysis import Analysis
from Configuration.ConfigManager import ConfigManager

sessions = ConfigManager.open_config("config")["race"]["api_sessions"]


@st.cache_data
def fetch_all_sessions(url: str) -> pd.DataFrame:
    """
    Loads all available race sessions. Makes website design.
    :param url: API with all race sessions.
    :return: Special data structure unique for streamlit lib.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_data = response.json()

        df = pd.DataFrame(raw_data)
        df_filtered = df[df['session_name'] == 'Race'].copy()
        df_filtered['Year'] = pd.to_datetime(df_filtered['date_start']).dt.year.astype(str)
        df_filtered['Race_Name'] = df_filtered['location'] + " (" + df_filtered['country_name'] + ")"

        return df_filtered[['session_key', 'Year', 'Race_Name', 'location']]
    except Exception as e:
        st.error(f"Data couldn't be loaded, something went wrong on OpenF1: {e}")
        return pd.DataFrame()


st.set_page_config(page_title="F1 Race Analysis", layout="wide")
st.title("F1 Race Analysis")

with st.spinner("Waiting for Stroll to finish, loading..."):
    all_sessions_df = fetch_all_sessions(sessions)

if all_sessions_df.empty:
    st.warning("Data couldn't be loaded from sessions API.")
    st.stop()

with st.sidebar:
    st.header("Race filter")

    available_years = sorted(all_sessions_df['Year'].unique(), reverse=True)
    selected_year = st.selectbox("Choose Year:", options=available_years)
    filtered_by_year_df = all_sessions_df[all_sessions_df['Year'] == selected_year]

    available_races = sorted(filtered_by_year_df['Race_Name'].unique())
    selected_race_name = st.selectbox("Choose Race:", options=available_races)

    final_selection = filtered_by_year_df[
        filtered_by_year_df['Race_Name'] == selected_race_name
        ]

    session_key_to_use = None
    if not final_selection.empty:
        session_key_to_use = str(final_selection['session_key'].iloc[0])
        st.info(f"Session key: **{session_key_to_use}**")

        run_analysis = st.button("Run Analysis", type="primary")
    else:
        st.warning("Cannot load data for this race.")
        run_analysis = False

if run_analysis and session_key_to_use:
    st.header(f"Race results {selected_race_name} ({selected_year})")

    with st.spinner(f'Loading race analysis...'):
        results = Analysis.parallel(session_key_to_use)

    if results and "Error" not in results[0]:
        results_df = pd.DataFrame(results)
        st.dataframe(
            results_df.set_index('Position'),
            use_container_width=True
        )

        csv_data = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download results in CSV",
            data=csv_data,
            file_name=f'{selected_year}_{selected_race_name.replace(" ", "_")}_results.csv',
            mime='text/csv',
        )

        st.success("Analysis finished. Ready to download.")

    elif results and "Error" in results[0]:
        st.error(f"Someone crashed, Red flag: {results[0]['Error']}")
    else:
        st.error("All DNFs, no Analysis available.")
