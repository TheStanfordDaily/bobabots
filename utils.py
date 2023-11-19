import os
import re
from datetime import datetime


def swap_files(file1, file2):
    if os.path.exists(file2):
        os.rename(file1, file2 + ".tmp")
        os.rename(file2, file1)
        os.rename(file2 + ".tmp", file2)


# Compare folders with files in another folder that contains files with the same names.
# Identify which file is larger for each pair; swap if necessary.
def compare_folders(path1, path2):
    for filename in os.listdir(path1):
        if filename.endswith(".html"):
            file1 = os.path.join(path1, filename)
            file2 = os.path.join(path2, filename)
            if os.path.exists(file2) and os.path.getsize(file1) < os.path.getsize(file2):
                # File 2 is larger than File 1. Swapping.
                swap_files(file2, file1)


def shell_script_append(path_in, path_out):
    valid_line = r"echo y \| vip @stanforddaily\.production -- wp post meta update \d+ rank_math_primary_category \d+"
    with open(path_in) as file_in:
        valid_lines = [x.strip() for x in file_in.readlines() if re.match(valid_line, x.strip())]
    with open(path_out, "a") as file_out:
        for index, line in enumerate(valid_lines):
            file_out.write(line + " &\n")
            if index % 4 == 0:
                file_out.write("wait")
            file_out.write("\n")


def load_env() -> tuple:
    pairs = {}
    with open(os.path.join(os.path.dirname(__file__), ".env")) as f:
        for line in f:
            key, value = line.split("=")
            pairs[key] = value.strip().replace('"', "")

    if "CLIENT_KEY" not in pairs or "CLIENT_SECRET" not in pairs:
        raise Exception("No CLIENT_KEY or CLIENT_SECRET in .env")

    return pairs["CLIENT_KEY"], pairs["CLIENT_SECRET"]


def itemize(items):
    len_items = len(items)
    if len_items == 0:
        return ""
    elif len_items == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def format_date(instance: datetime, verbose=False) -> str:
    """
    Formats a datetime instance into a string following AP style.

    Args:
    instance (datetime): The datetime instance to format.
    verbose (bool): Whether to include the time in the formatted string.

    Returns:
    str: A string representation of the date.
    """
    months = ["Jan.", "Feb.", "March", "April", "May", "June",
              "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]

    formatted_month = months[instance.month - 1]
    formatted_day = instance.day
    formatted_year = instance.year

    if verbose:
        formatted_hours = instance.hour % 12
        formatted_hours = formatted_hours if formatted_hours else 12
        formatted_minutes = f"{instance.minute:02d}"
        formatted_meridian = "a.m." if instance.hour < 12 else "p.m."

        return f"{formatted_month} {formatted_day}, {formatted_year}, {formatted_hours}:{formatted_minutes} {formatted_meridian}"
    else:
        return f"{formatted_month} {formatted_day}, {formatted_year}"


def iso_to_ap(iso: str) -> str:
    iso_date = datetime.fromisoformat(iso)
    return format_date(iso_date, verbose=True)
