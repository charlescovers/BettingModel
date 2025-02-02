import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import streamlit as st

# Function to scrape BartTorvik team efficiency data
def scrape_barttorvik():
    url = "https://barttorvik.com/trank.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame({
            "Team": ["Sample Team A", "Sample Team B"],
            "AdjO": [110.5, 108.3],
            "AdjD": [98.2, 100.4],
            "Tempo": [70.1, 68.5],
            "SOS": [1.5, 2.0]
        })
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ratings-table"})
    if not table:
        return pd.DataFrame({
            "Team": ["Sample Team A", "Sample Team B"],
            "AdjO": [110.5, 108.3],
            "AdjD": [98.2, 100.4],
            "Tempo": [70.1, 68.5],
            "SOS": [1.5, 2.0]
        })
    
    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        try:
            team_name = cols[1].text.strip()
            adj_o = float(cols[4].text.strip())  # Adjusted Offense
            adj_d = float(cols[5].text.strip())  # Adjusted Defense
            tempo = float(cols[7].text.strip())  # Tempo
            sos = float(cols[14].text.strip())   # Strength of Schedule
            data.append([team_name, adj_o, adj_d, tempo, sos])
        except (ValueError, IndexError):
            continue
    
    return pd.DataFrame(data, columns=["Team", "AdjO", "AdjD", "Tempo", "SOS"])

# Streamlit App
def main():
    st.title("CharlesCovers - College Basketball Analytics")
    
    st.subheader("Team Tempo vs Offensive Efficiency")
    bart_data = scrape_barttorvik()
    
    if bart_data.empty:
        st.error("Error fetching data")
    else:
        fig = px.scatter(bart_data, x="Tempo", y="AdjO", title="Team Tempo vs Offensive Efficiency",
                         labels={"Tempo": "Possessions per Game", "AdjO": "Adjusted Offensive Efficiency"})
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
