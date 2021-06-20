# load dependencies
import requests
import pandas as pd
import seaborn as sns
from bs4 import BeautifulSoup
from datetime import date, datetime

headers = {"User-Agent": "Jan D. <jan.d@correlaid.org>"}


def fetch_ags() -> pd.DataFrame:
    """
    Fetch Amtliche Gemeindeschlüssel for Thüringen and return the table as a pandas' DataFrame.

    :return: DataFrame including the Amtliche Gemeindeschlüssel for Thüringen
    :rtype: pd.DataFrame
    """

    # define URL
    url = "https://statistik.thueringen.de/datenbank/gemauswahl.asp"
    # GET request with pre-defined URL
    response = requests.get(url=url, headers=headers)
    # parse HTML using BeautifulSoup
    soup = BeautifulSoup(markup=response.text, features="html.parser")
    # find all table tags
    table = soup.find(name="table")
    # parse table headers by identifying th-tag
    table_headers = [th.text for th in table.find(name="thead").find_all("th")]
    # initialize empty array
    rows = []
    # loop over rows and extract values
    for row in soup.find(name="tbody").find_all(name="tr"):
        element = {}
        for i, col in enumerate(row.find_all(name="td")):
            element[table_headers[i]] = col.text
        rows.append(element)
    # return data as data frame
    return pd.DataFrame.from_records(data=rows)


def fetch_incidence(ags: str) -> pd.DataFrame:
    """
    Fetch the Corona incidences for a given region identified by AGS.

    :param ags: Amtlicher Gemeindeschlüssel
    :type ags: str
    :return: DataFrame with the historical incidences
    :rtype: pd.DataFrame
    """
    # build url
    url = f"https://api.corona-zahlen.org/districts/{ags}/history/incidence"
    # GET request
    response = requests.get(url=url, headers=headers)
    # parse and extract data
    data = response.json()["data"]
    # reformat data: parse date and rename fields
    incidences = [{"date": date.fromisoformat(e["date"][:10]), "incidence": e["weekIncidence"]} for
                  e in data[ags]["history"]]
    # transform data into a data frame
    df_incidences = pd.DataFrame.from_records(data=incidences)
    # set index to date to ease merging
    df_incidences = df_incidences.set_index(keys="date")
    return df_incidences


def fetch_weather_data(id_: str, end_date: date) -> pd.DataFrame:
    """
    Fetch weather data from www.wetterkontor.de. Always returns data for the last 8 weeks.

    :param id_: Id of the weather station
    :type id_: str
    :param end_date: Last date of the time period
    :type end_date: date
    :return: DataFrame including weather data for each day
    :rtype: pd.DataFrame
    """
    # define base url
    url = "https://www.wetterkontor.de/de/wetter/deutschland/rueckblick.asp"
    # define query parameters
    query_parameters = {
        "id": id_,
        "t": "8",
        "datum": end_date
    }
    # GET request
    response = requests.get(url=url, params=query_parameters, headers=headers)
    # parse HTML using BeautifulSoup
    soup = BeautifulSoup(markup=response.text, features="html.parser")
    # parse table body for table with #extremwerte
    table = soup.find(name="table", attrs={"id": "extremwerte"}).find(name="tbody")
    # initialize empty list
    values = []
    # loop over rows and extract values
    for row in table.find_all(name="tr"):
        columns = row.find_all(name="td")
        if len(columns) > 0:
            values.append({
                "date": datetime.strptime(columns[0].text, "%d.%m.%Y").date(),
                "precipitation": float(columns[4].text.replace(",", ".")),
                "min_temperature": float(columns[1].text.replace(",", ".")),
                "max_temperature": float(columns[2].text.replace(",", ".")),
                "avg_temperature": float(columns[3].text.replace(",", ".")),
            })
    # transform data into a data frame
    df = pd.DataFrame.from_records(data=values)
    # set index to date to ease merging
    df = df.set_index(keys="date")
    return df


df_incidences = fetch_incidence(ags="16053")
df_weather = fetch_weather_data(id_="M552",
                                end_date=date.fromisoformat("2021-03-31"))

g = sns.relplot(x="date", y="incidence", kind="line", data=df_incidences)
g.fig.autofmt_xdate()

df = df_weather.merge(right=df_incidences, right_index=True, left_index=True)
df = df.reset_index()

sns.lineplot(x='date', y='value', hue='variable',
             data=pd.melt(df, ["date"]))
