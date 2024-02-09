import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd
from string import ascii_uppercase
import json
from tqdm import tqdm
from Levenshtein import distance

with open("subjects.json") as file:
    subject_abbreviations = json.load(file)
    subject_abbreviations["Undeclared"] = "Undeclared"

with open("roster-urls.json") as file:
    roster_urls = json.load(file)


def player_profile(url: str) -> dict:
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "html.parser")
    sidearm = soup.find("div", class_="sidearm-roster-player-fields")

    if sidearm is None:
        return {}

    try:
        major = sidearm.find("dt", text="Major").find_next_sibling("dd").text
        name_sidearm = soup.find("span", class_="sidearm-roster-player-name")
        first_name = name_sidearm.find("span", class_="sidearm-roster-player-first-name").text
        last_name = name_sidearm.find("span", class_="sidearm-roster-player-last-name").text
        academic_class = sidearm.find("dt", text="Class").find_next_sibling("dd").text
    except AttributeError:
        print(f"Failed to process {url}; skipping...")
        return {}

    return {
        "First Name": first_name,
        "Last Name": last_name,
        "Class": academic_class,
        "Major": major,
    }


def roster_dataset(url: str) -> pd.DataFrame:
    if url == roster_urls["men"]["football"]:
        try:
            with open("football.html") as file:
                html_content = file.read()
        except FileNotFoundError:
            return pd.DataFrame()
    else:
        html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "html.parser").find("div", class_="sidearm-roster-templates-container").find("section").find("ul", class_="sidearm-roster-players")

    # Find all rows representing players on the team.
    players = soup.find_all("li", class_="sidearm-roster-player")
    player_data = []

    for player in tqdm(players):
        player_url = player["data-player-url"]
        profile = player_profile(f"https://gostanford.com{player_url}")
        profile["URL"] = player_url
        player_data.append(profile)

    return pd.DataFrame(player_data)


def insert_abbreviations(path):
    df = pd.read_csv(path)
    abbrevs = []

    for index, row in df.iterrows():
        if row["Major"] not in subject_abbreviations:
            if row.isna().any():
                abbrevs.append("")
                continue
            print(f"Unknown major: {row['Major']}")
            close_matches = list(filter(lambda s: distance(row["Major"], s) < 10, subject_abbreviations.keys()))
            close_matches.sort(key=lambda s: distance(row["Major"], s))
            if len(close_matches) > 0:
                abbrevs.append(subject_abbreviations[close_matches[0]])
                print("abbreviation successful", close_matches[0])
            else:
                abbrevs.append("")
            continue

        abbrevs.append(subject_abbreviations[row["Major"]])

    df.insert(4, "Major (Abbreviated)", abbrevs, allow_duplicates=True)
    df.to_csv(path, index=False)
