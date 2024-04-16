import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
from Levenshtein import distance
from glob import glob

with open("subjects.json") as subjects_file:
    subject_abbreviations = json.load(subjects_file)
    subject_abbreviations["Undeclared"] = "Undeclared"

with open("roster-years.json") as roster_file:
    roster_urls = json.load(roster_file)


def player_profile(url: str) -> dict:
    response = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser")
    sidearm = soup.find("div", class_="sidearm-roster-player-fields") or soup.find("div", class_="sidearm-roster-player-header-details")

    if sidearm is None:
        return {}

    major_abbrev = ""

    try:
        major = sidearm.find("dt", text="Major").find_next_sibling("dd").text
        if major in subject_abbreviations:
            major_abbrev = subject_abbreviations[major]
        else:
            close_matches = list(filter(lambda s: distance(major, s) < 10, subject_abbreviations.keys()))
            close_matches.sort(key=lambda s: distance(major, s))
            if len(close_matches) > 0:
                major_abbrev = subject_abbreviations[close_matches[0]]
    except AttributeError:
        major = ""

    first_name = soup.find("span", class_="sidearm-roster-player-first-name").text
    last_name = soup.find("span", class_="sidearm-roster-player-last-name").text
    academic_class = soup.find("dt", text="Class").find_next_sibling("dd").text

    return {
        "First Name": first_name,
        "Last Name": last_name,
        "Class": academic_class,
        "Major": major,
        "Major (Abbreviated)": major_abbrev,
    }


def roster_url(sport: str, year: int) -> str:
    return f"https://gostanford.com/sports/{sport}/roster/{year}"


def roster_dataset(url: str, description: str | None = None, mode: str | None = None) -> pd.DataFrame:
    html_content = requests.get(url).text
    if mode == "men":
        soup = BeautifulSoup(html_content, "html.parser").find("div", class_="sidearm-roster-templates-container").find("section", attrs={"aria-label": "Men's Player Roster"}).find("ul", class_="sidearm-roster-players")
    elif mode == "women":
        soup = BeautifulSoup(html_content, "html.parser").find("div", class_="sidearm-roster-templates-container").find("section", attrs={"aria-label": "Women's Player Roster"}).find("ul", class_="sidearm-roster-players")
    else:
        soup = BeautifulSoup(html_content, "html.parser").find("div", class_="sidearm-roster-templates-container").find("section").find("ul", class_="sidearm-roster-players")
    # Find all rows representing players on the team.
    players = soup.find_all("li", class_="sidearm-roster-player")
    player_data = []

    for player in tqdm(players, description):
        player_url = player["data-player-url"]
        profile = player_profile(f"https://gostanford.com{player_url}")
        profile["URL"] = player_url
        player_data.append(profile)

    return pd.DataFrame(player_data)


def roster_table(url: str) -> pd.DataFrame:
    response = requests.get(f"{url}?view=2", allow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser").find("div", class_="sidearm-roster-grid-template-1")
    # Find table with "Roster" in caption.
    table = soup.find("caption", text=lambda text: "Roster" in text).find_parent("table")
    headers = [th.text for th in table.thead.find_all("th")]

    if "Major" in headers:
        major_index = headers.index("Major")
    else:
        print(f"Major not found in {url}")
        return pd.DataFrame()

    headers.insert(major_index + 1, "Major (Abbreviated)")
    data = []

    for tr in table.tbody.find_all("tr"):
        row = [td.text.strip() for td in tr.find_all("td")]
        major_abbrev = ""
        major = row[major_index]
        close_matches = list(filter(lambda s: distance(major, s) < 10, subject_abbreviations.keys()))
        close_matches.sort(key=lambda s: distance(major, s))
        if len(close_matches) > 0 and major:
            major_abbrev = subject_abbreviations[close_matches[0]]
        row.insert(major_index + 1, major_abbrev)
        data.append(row)

    return pd.DataFrame(data, columns=headers)


def simplified_majors(major_counts):
    # Sort and identify the top 10 most common majors.
    top_majors = major_counts.sort_values("Total Athletes", ascending=False).head(10)

    # Find majors to be grouped into "Other" category.
    mask = ~major_counts["Major"].isin(top_majors["Major"])
    others_sum = major_counts[mask]["Total Athletes"].sum()

    # Create a new row for "Other" majors.
    other_row = pd.DataFrame(data={"Major": ["Other"], "Total Athletes": [others_sum]})

    # Combine top majors with "Other" category.
    result = pd.concat([top_majors, other_row], ignore_index=True).sort_values("Total Athletes", ascending=False)

    return result


def format_to_flourish():
    # Define patterns for each folder.
    patterns = ["men/*.csv", "women/*.csv", "mixed/*.csv"]
    year_columns = ["Class", "Academic Year"]
    list_of_dfs = []

    for pattern in patterns:
        csv_files = glob(pattern)
        for filename in csv_files:
            df = pd.read_csv(filename)

            for col in year_columns:
                if col in df.columns:
                    # Filter out rows where "Gr" or "gr" appear in the specified column.
                    df = df[~df[col].str.contains("Gr", case=False, na=False)]
                    break  # Stop checking once the relevant column is found and filtered.

            # Extract the sport from the URL.
            df["Sport"] = filename[filename.index("/") + 1:filename.index(".")]
            list_of_dfs.append(df)

    # Concatenate all DataFrames into a single DataFrame.
    all_data = pd.concat(list_of_dfs, ignore_index=True)

    # Use "Major (Abbreviated)" if it's not empty; otherwise use "Major" field.
    all_data["Major"] = all_data.apply(lambda x: x["Major (Abbreviated)"] if x["Major (Abbreviated)"] != "" else x["Major"], axis=1)

    # Group the data by "Major" and count the total number of athletes.
    major_counts = all_data.groupby("Major").size().reset_index(name="Total Athletes")

    simplified = simplified_majors(major_counts)
    simplified.to_csv("simplified_majors.csv", index=False)

    # Sort by "Major" field.
    sorted_major_counts = major_counts.sort_values("Major")
    sorted_major_counts.to_csv("major_counts.csv", index=False)

    # Group the data by "Major" and "Sport" and count the occurrences.
    grouped_data = all_data.groupby(["Major", "Sport"]).size().reset_index(name="Count")

    # Pivot the table to have majors as rows and sports as columns.
    pivot_table = grouped_data.pivot(index="Major", columns="Sport", values="Count").drop("Undeclared")

    # Sort the DataFrame by "Major" and export.
    sorted_pivot_table = pivot_table.sort_index()
    sorted_pivot_table.to_csv("majors_and_sports.csv")


def write_sport(group_name, sport, year, mode = None):
    url = roster_url(sport, year)
    # Use roster_table for all sports except men's tennis, artistic swimming, cross country and sailing.
    if sport in ["mens-tennis", "artswim", "cross-country", "sailing", "fencing", "track-and-field"]:
        df = roster_dataset(url, sport, mode)
    else:
        df = roster_table(url)
    df.to_csv(f"{group_name}/{sport}.csv", index=False)


def write_datasets():
    for group_name, roster_group in roster_urls.items():
        for sport, year in roster_group.items():
            write_sport(group_name, sport, year)


if __name__ == "__main__":
    write_sport("men", "mens-rowing", 2024)
    # for group in ["men", "women"]:
    #     write_sport(group, "track-and-field", 2024, group)

# in the legend, put indicator for number of people on the team