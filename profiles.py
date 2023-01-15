import re
import os
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup

FOLDER_PATH = "..\\..\\departments"  # Type actual directory here.


class Profile:
    def __init__(self, name, user_id, email, phone, role, affiliation, department):
        self.name = name.text if name else None
        self.user_id = user_id
        self.email = email
        self.phone = phone
        self.role = role.text if role else None
        self.affiliation = affiliation.text if affiliation else None
        self.department = department.text if department else None


def parse_files(folder_path):
    result = []

    for filename in tqdm(os.listdir(folder_path), desc="Parsing files"):
        if filename.endswith(".html"):
            with open(os.path.join(folder_path, filename), "rb") as file:
                soup = BeautifulSoup(file, "html5lib")
            for person in soup.find_all("li", attrs={"class": "people__list__item"}):
                person_vcard_list = person.find("ul", attrs={"class": "list__reset person__vcard__list"})
                vcard_items = [(x.find("span", attrs={"class": "sidebar-label"}).text, x.find("span", attrs={"sidebar-detail"}).text) for x in person_vcard_list.find_all("li", attrs={"class": "person__vcard__list__item"})]
                email_addr_regex = re.compile(r".+@.+\..+")
                phone_regex = re.compile(r"\(\d{3}\) \d{3}-\d{4}")
                email = None
                phone = None
                user_id = None

                for label, value in vcard_items:
                    if email_addr_regex.match(value):
                        email = value
                    if phone_regex.match(value):
                        phone = value
                    if label == "SI:":
                        user_id = value

                main_data = person.find("div", attrs={"class": "person__data__main"})
                name = main_data.find("a", attrs={"class": "person__data__name"})
                role = main_data.find("div", attrs={"class": "person__data__role__title"})
                affiliation = main_data.find("div", attrs={"class": "person__data__affiliation"})
                department = main_data.find("div", attrs={"class": "person__data__department"})

                result.append(Profile(name, user_id, email, phone, role, affiliation, department))

    return result


def write_profiles(profiles):
    with open("profiles.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "SUNet ID", "Email", "Phone", "Role", "Affiliation", "Department"])
        for profile in profiles:
            writer.writerow([profile.name, profile.user_id, profile.email, profile.phone, profile.role, profile.affiliation, profile.department])

if __name__ == "__main__":
    p = parse_files(FOLDER_PATH)
    write_profiles(p)