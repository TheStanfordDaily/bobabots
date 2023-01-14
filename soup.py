from bs4 import BeautifulSoup
import re


class Profile:
    def __init__(self, name, role, affiliation, department, email, phone, sunet_id):
        self.name = name.text if name else None
        self.role = role.text if role else None
        self.affiliation = affiliation.text if affiliation else None
        self.department = department.text if department else None
        self.email = email
        self.phone = phone
        self.sunet_id = sunet_id

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.affiliation} - {self.department} - {self.email} - {self.phone} - {self.sunet_id}"

    def __repr__(self):
        return self.__str__()

filepath = "{ENTER FILE PATH HERE}"

with open(filepath, "r") as file:
    soup = BeautifulSoup(file, "html.parser")
    for person in soup.find_all("li", attrs={"class": "people__list__item"}):
        person_vcard_list = person.find("ul", attrs={"class": "list__reset person__vcard__list"})
        vcard_items = [(x.find("span", attrs={"class": "sidebar-label"}).text, x.find("span", attrs={"sidebar-detail"}).text) for x in person_vcard_list.find_all("li", attrs={"class": "person__vcard__list__item"})]
        email_addr_regex = re.compile(r".+@.+\..+")
        phone_regex = re.compile(r"\(\d{3}\) \d{3}-\d{4}")
        email = None
        phone = None
        sunet_id = None

        for label, value in vcard_items:
            if email_addr_regex.match(value):
                email = value
            if phone_regex.match(value):
                phone = value
            if label == "SI:":
                sunet_id = value

        main_data = person.find("div", attrs={"class": "person__data__main"})
        name = main_data.find("a", attrs={"class": "person__data__name"})
        role = main_data.find("div", attrs={"class": "person__data__role__title"})
        affiliation = main_data.find("div", attrs={"class": "person__data__affiliation"})
        department = main_data.find("div", attrs={"class": "person__data__department"})

        result = Profile(name, role, affiliation, department, email, phone, sunet_id)
        print(result)