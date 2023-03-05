# example url: https://explorecourses.stanford.edu/search?q=EARTHSYS&view=catalog&page=0&academicYear=&filter-term-Winter=on&filter-term-Spring=on&filter-instructionmode-INPERSON=on&filter-instructionmode-INDEPENDENTSTDY=on&filter-units-5=on&filter-time-3=on&filter-time-4=on&filter-day-2=on&filter-day-4=on&filter-ger-WAYAQR=on&filter-ger-WAYSMA=on&filter-component-LEC=on&filter-component-SEM=on&filter-academiclevel-UG=on&filter-academiclevel-GR=on&collapse=%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C&filter-departmentcode-EARTHSYS=on&filter-catalognumber-EARTHSYS=on&filter-coursestatus-Active=on&filter-catalognumber-EARTHSYS=on
from typing import Optional
from enum import Enum

class ExploreCourses:
    def __init__(self, query: str, page: int, academic_year: str = "", term_offered: Optional[str] = None, instruction_mode: str = "", units: str = "", time: str = "", day: str = "", ger: str = "", component: str = "", academic_level: str = "", department_code: str = "", catalog_number: str = "", course_status: str = "", collapse: str = ""):
        # https://explorecourses.stanford.edu/search?filter-units-5=on&filter-term-Winter=on&filter-day-2=on&filter-component-LEC=on&filter-instructionmode-INDEPENDENTSTDY=on&filter-day-4=on&filter-catalognumber-EARTHSYS=on&filter-academiclevel-GR=on&filter-academiclevel-UG=on&filter-instructionmode-INPERSON=on&filter-ger-WAYAQR=on&q=EARTHSYS&view=catalog&filter-component-SEM=on&filter-time-4=on&filter-time-3=on&filter-ger-WAYSMA=on&filter-term-Spring=on&page=0&filter-coursestatus-Active=on&filter-departmentcode-EARTHSYS=on&collapse=%2c2%2c3%2c4%2c5%2c6%2c7%2c8%2c&academicYear=20212022
        self.results = []

    def search(self) -> list:
        pass

    @classmethod
    def from_url(cls, url: str) -> "ExploreCourses":
        pass

# https://explorecourses.stanford.edu/search?q=EARTHSYS&view=catalog&page=0&academicYear=20212022&filter-instructionmode-INPERSON=on&filter-instructionmode-INDEPENDENTSTDY=on&filter-units-5=on&filter-time-3=on&filter-time-4=on&filter-day-2=on&filter-day-4=on&filter-ger-WAYAQR=on&filter-ger-WAYSMA=on&filter-component-LEC=on&filter-component-SEM=on&filter-academiclevel-UG=on&filter-academiclevel-GR=on&collapse=%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2C&filter-departmentcode-EARTHSYS=on&filter-catalognumber-EARTHSYS=on&filter-coursestatus-Active=on&filter-catalognumber-EARTHSYS=on