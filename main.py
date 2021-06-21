# load dependencies
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

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
    # parse table headers by identifying th-tag
    table_headers = [th.text for th in soup.find(name="thead").find_all("th")]
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


def fetch_weather_data(id_: str, end_date: date) -> list[dict]:
    """
    Fetch weather data from www.wetterkontor.de. Always returns data for the last 8 weeks.

    :param id_: Id of the weather station
    :type id_: str
    :param end_date: Last date of the time period
    :type end_date: date
    :return: List of dictionaries including weather data for each day
    :rtype: list[dict]
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
    return values


def fetch_weather_data_time_period(id_: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Fetch weather data for a given time period using fetch_weather_data function.

    :param id_: Id of the weather station
    :type id_: str
    :param start_date: First date of the time period
    :type start_date: date
    :param end_date: Last date of the time period
    :type end_date: date
    :return: DataFrame including weather data for each day
    :rtype: pd.DataFrame
    """
    # initialize empty list
    values = []
    # execute until data for each data are available
    while start_date not in [e["date"] for e in values]:
        end_date = min([e["date"] for e in values]) - timedelta(days=1) if len(values) else end_date
        values += fetch_weather_data(id_=id_, end_date=end_date)
    # transform data into a data frame
    df = pd.DataFrame.from_records(data=values)
    # set index to date to ease merging
    df = df.set_index(keys="date")
    return df


def plot_two_axes(df: pd.DataFrame,
                  x: str,
                  y1: str,
                  y2: str,
                  y1_color: str = "#92de3f",
                  y2_color: str = "#3862a2",
                  font_color: str = "#444444") -> None:
    """
    Plot two variables with the same x-axis and use two different axes.

    :param df: DataFrame to use to plot
    :type df: pd.DataFrame
    :param x: X-axis column
    :type x: str
    :param y1: Y1-axis column
    :type y1: str
    :param y2: Y2-axis column
    :type y2: str
    :param y1_color: Color of y1-line
    :type y1_color: str
    :param y2_color: Color of y2-line
    :type y2_color: str
    :param font_color: Font color
    :type font_color: str
    :return: None
    :rtype: None
    """
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(xlabel=x.capitalize(), color=font_color)
    ax1.set_ylabel(ylabel=y1.capitalize(), color=y1_color)
    ax1.plot(df[x], df[y1], color=y1_color)
    ax1.tick_params(axis="y", labelcolor=y1_color)
    ax1.tick_params(axis="x", labelcolor=font_color)
    # instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel(ylabel=y2.capitalize(), color=y2_color)
    ax2.plot(df[x], df[y2], color=y2_color)
    ax2.tick_params(axis="y", labelcolor=y2_color)
    ax2.spines["bottom"].set_color(font_color)
    ax2.spines["top"].set_color(font_color)
    ax2.spines["right"].set_color(font_color)
    ax2.spines["left"].set_color(font_color)
    fig.tight_layout()
    plt.show()


# fetch ags, incidences and weather data
df_ags = fetch_ags()
df_incidences = fetch_incidence(ags="16053")
df_weather = fetch_weather_data_time_period(id_="M552",
                                            start_date=date.fromisoformat("2020-03-20"),
                                            end_date=date.fromisoformat("2021-06-19"))
# save data frames to CSV
df_ags.to_csv(path_or_buf="data/ags.csv")
df_incidences.to_csv(path_or_buf="data/incidences.csv")
df_weather.to_csv(path_or_buf="data/weather.csv")

# join incidences and weather data
df = df_weather.merge(right=df_incidences, right_index=True, left_index=True)
df = df.reset_index()

# add days
df["day"] = list(range(1, len(df) + 1))[::-1]

# plot incidences and average temperature
plot_two_axes(df=df, x="day", y1="incidence", y2="avg_temperature")

# plot incidences and precipitation
plot_two_axes(df=df, x="day", y1="incidence", y2="precipitation")
