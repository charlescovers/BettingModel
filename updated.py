import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
KENPOM_USERNAME = os.getenv("KENPOM_USERNAME")
KENPOM_PASSWORD = os.getenv("KENPOM_PASSWORD")

# KenPom login URL
LOGIN_URL = "https://kenpom.com/login.php"

def scrape_kenpom_authenticated():
    session = requests.Session()
    
    # Login payload
    payload = {
        "email": KENPOM_USERNAME,
        "password": KENPOM_PASSWORD
    }
    
    # Perform login
    session.post(LOGIN_URL, data=payload)
    
    # Fetch KenPom ratings page (after login)
    ratings_url = "https://kenpom.com/"
    response = session.get(ratings_url)
    
    if response.status_code != 200:
        st.error("Failed to access KenPom after login.")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ratings-table"})
    rows = table.find_all("tr")[1:]  # Skip header row
    
    kenpom_data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        rank = int(cols[0].text.strip())
        team = cols[1].text.strip()
        adj_off = float(cols[4].text.strip())  # Adjusted Offensive Efficiency
        adj_def = float(cols[6].text.strip())  # Adjusted Defensive Efficiency
        tempo = float(cols[8].text.strip())   # Tempo
        luck = float(cols[10].text.strip())   # Luck factor

        kenpom_data.append([rank, team, adj_off, adj_def, tempo, luck])

    df_kenpom = pd.DataFrame(
        kenpom_data, columns=["Rank", "Team", "AdjO", "AdjD", "Tempo", "Luck"]
    )
    
    return df_kenpom

# Streamlit UI
st.title("KenPom Data Scraper")

if st.button("Scrape KenPom Data"):
    df_kenpom = scrape_kenpom_authenticated()
    if df_kenpom is not None:
        # Save to a CSV file with today's date
        today = datetime.today().strftime("%Y-%m-%d")
        filename = f"kenpom_data_{today}.csv"
        df_kenpom.to_csv(filename, index=False)
        st.success(f"Saved KenPom data to {filename}")
        st.dataframe(df_kenpom)
