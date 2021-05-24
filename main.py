# load dependencies
import requests
import pandas as pd
from bs4 import BeautifulSoup

# define URL
url = "https://statistik.thueringen.de/datenbank/gemauswahl.asp"

response = requests.get(url=url)

soup = BeautifulSoup(markup=response.text, features="html.parser")
table = soup.find(name="table")
headers = [th.text for th in soup.find(name="thead").find_all("th")]

rows = []
for row in soup.find(name="tbody").find_all(name="tr"):
    element = {}
    for i, col in enumerate(row.find_all(name="td")):
        element[headers[i]] = col.text
    rows.append(element)

df_ags = pd.DataFrame.from_records(data=rows)

base_url = "https://api.corona-zahlen.org/districts/16053/history/incidence"
response = requests.get(url=base_url)
data = response.json()["data"]
