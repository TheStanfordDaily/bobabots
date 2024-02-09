import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import pandas as pd
from string import ascii_uppercase
import json
from tqdm import tqdm
from Levenshtein import distance
from glob import glob

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
    except AttributeError:
        major = "Undeclared"

    name_sidearm = soup.find("span", class_="sidearm-roster-player-name")
    first_name = name_sidearm.find("span", class_="sidearm-roster-player-first-name").text
    last_name = name_sidearm.find("span", class_="sidearm-roster-player-last-name").text
    academic_class = sidearm.find("dt", text="Class").find_next_sibling("dd").text

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

# for group_name, roster_group in roster_urls.items():
#     for sport, url in roster_group.items():
#         df = roster_dataset(url)
#         df.to_csv(f"{group_name}/{sport}.csv", index=False)
#         insert_abbreviations(f"{group_name}/{sport}.csv")

# Step 1: Read all CSV files into pandas DataFrames

# Define patterns for each folder
patterns = ['men/*.csv', 'women/*.csv', 'mixed/*.csv']

list_of_dfs = []

for pattern in patterns:
    csv_files = glob(pattern)
    for filename in csv_files:
        df = pd.read_csv(filename)

        # Filter out rows where "Class" contains "Graduate" or "graduate"
        df = df[~df['Class'].str.contains("Graduate", case=False)]

        # Extract the sport from the URL
        df['Sport'] = df['URL'].apply(lambda x: x.split('/')[2].replace('-', ' ').title())
        list_of_dfs.append(df)


def simplified_majors():
    all_data = pd.concat(list_of_dfs, ignore_index=True)

    # Filter out "Undeclared" majors
    all_data = all_data[all_data['Major (Abbreviated)'] != 'Undeclared']

    # Use "Major (Abbreviated)" if it's not empty, otherwise use "Major"
    all_data['Major'] = all_data.apply(
        lambda x: x['Major (Abbreviated)'] if x['Major (Abbreviated)'] != '' else x['Major'], axis=1)

    # Group the data by 'Major' and count the total number of athletes
    major_counts = all_data.groupby('Major').size().reset_index(name='Total Athletes')

    # Sort and identify the top 10 most common majors
    top_majors = major_counts.sort_values('Total Athletes', ascending=False).head(10)

    # Find majors to be grouped into "Other"
    mask = ~major_counts['Major'].isin(top_majors['Major'])
    others_sum = major_counts[mask]['Total Athletes'].sum()

    # Create a new row for "Other" majors
    other_row = pd.DataFrame(data={'Major': ['Other'], 'Total Athletes': [others_sum]})

    # Combine top majors with "Other"
    result = pd.concat([top_majors, other_row], ignore_index=True).sort_values('Total Athletes', ascending=False)

    return result

# Concatenate all DataFrames into a single DataFrame
all_data = pd.concat(list_of_dfs, ignore_index=True)

# Use "Major (Abbreviated)" if it's not empty; otherwise use "Major"
all_data['Major'] = all_data.apply(lambda x: x['Major (Abbreviated)'] if x['Major (Abbreviated)'] != '' else x['Major'],
                                   axis=1)

# Group the data by 'Major' and count the total number of athletes
major_counts = all_data.groupby('Major').size().reset_index(name='Total Athletes')

simplified_majors = simplified_majors()
simplified_majors.to_csv('simplified_majors.csv', index=False)

# Sort by 'Major'
sorted_major_counts = major_counts.sort_values('Major')
sorted_major_counts.to_csv('major_counts.csv', index=False)

# Group the data by 'Major' and 'Sport' and count the occurrences.
grouped_data = all_data.groupby(['Major', 'Sport']).size().reset_index(name='Count')

# Pivot the table to have majors as rows and sports as columns.
pivot_table = grouped_data.pivot(index='Major', columns='Sport', values='Count').drop("Undeclared")

# Sort the DataFrame by 'Major' and export
sorted_pivot_table = pivot_table.sort_index()
sorted_pivot_table.to_csv('majors_and_sports.csv')
