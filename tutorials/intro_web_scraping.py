# Web scraping is a method of automating data collection from a site.
# It's prone to error, so if the data is available for download or at an XML or JSON endpoint,
# go with that option before resorting to this. Otherwise, you'll have to update the script over and over.
# It's not a long-term solution and is best for cases when you just need to run it once to get the data
# and apply it to some other project.

# Getting Started
import csv
import requests
from bs4 import BeautifulSoup
page = requests.get("https://stanford.edu")
soup = BeautifulSoup(page.content, "html.parser")
print(soup.prettify())

# What kind of "object" are you trying to collect? # How do we collect them?


class Professor:
    def __init__(self, name, email_address, headshot_url, profile_url):
        self.name = name
        self.email_address = email_address
        self.headshot_url = headshot_url
        self.profile_url = profile_url


serdar = Professor("Serdar Tumgoren", "tumgoren@stanford.edu",
                   "https://comm.stanford.edu/sites/g/files/sbiybj22231/files/styles/medium_square/public/media/image/tumgoren_0.jpg",
                   "https://comm.stanford.edu/people/serdar-tumgoren")

# HTML of Interest
# Next step is to find one of the HTML elements in a list on the site and identify its patterns.
# In this case, we’re looking for `div` tags with the `paragraph_row` class.
# We can use the Chrome Developer Tools to identify appropriate specifications for the elements we want.

# <div class="paragraph_row">
#   <div class="paragraph-row node-stanford-page-row su-page-components entity-reference-revisions label-hidden react-paragraphs-row container-1-items flex-container" data-item-count="1">
#     <div class="paragraph-item ptype-stanford-wysiwyg flex-12-of-12" data-react-columns="12">
#       <div class="paragraph paragraph--type--stanford-wysiwyg paragraph--view-mode--default">
#         <div class="su-wysiwyg-text paragraph stanford-wysiwyg text-long label-hidden">
#           <h2>Serdar Tumgoren</h2>
#           <div class="align-right media-entity-wrapper image">
#             <div class="media image field-media-image label-hidden">
#               <img loading="lazy" src="/sites/g/files/sbiybj22231/files/styles/medium_square/public/media/image/tumgoren_0.jpg?h=90cbfd2a&amp;itok=shDu-Ucc" width="220" height="220" alt="Serdar Tumgoren" />
#             </div>
#           </div>
#           <p>Lorry I. Lokey Visiting Professor in Professional Journalism <br />
#             <a href="mailto:tumgoren@stanford.edu">tumgoren@stanford.edu</a>
#             <br /> 650.725.7092 <br /> McClatchy Hall, Rm. 342
#           </p>
#           <p>Tumgoren is passionate about open source tools and platforms that help journalists uncover data-driven stories.</p>
#           <p>
#             <a class="su-button" data-entity-substitution="canonical" data-entity-type="node" data-entity-uuid="1f381813-3947-4ab9-b4a3-d65dbcf1523d" href="/people/serdar-tumgoren" title="Serdar Tumgoren">More</a>
#           </p>
#         </div>
#       </div>
#     </div>
#   </div>
# </div>

# Now let's get to the real deal, shall we?


def block_fields(block):
    try:
        name = block.find("h2").text
    except IndexError:
        return
    try:
        email_address = block.find("a").text
    except TypeError:
        email_address = None
    headshot_url = block.find("img")["src"]
    try:
        profile_url = block.find_all("a", attrs={"class": "su-button"})[0]["href"]
    except IndexError:
        profile_url = None

    return Professor(name, email_address, headshot_url, profile_url)


comm = requests.get("https://comm.stanford.edu/people/faculty")
comm_soup = BeautifulSoup(comm.content, "html.parser")


def export_to_csv(headers, data):
    with open("professors.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for entry in data:
            writer.writerow([entry.name, entry.email_address, entry.headshot_url, entry.profile_url])


professor_data = filter(lambda p: p is not None, map(block_fields, comm_soup.find_all("div", attrs={"class": "paragraph_row"})))
professor_headers = ["Name", "Email", "Headshot", "Profile"]

export_to_csv(professor_headers, professor_data)  # Viola!
