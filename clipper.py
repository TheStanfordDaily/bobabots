import os
import re
import requests
import sys
from pylatex import Document, Package, Command, Figure
from pylatex.utils import italic, NoEscape
from bs4 import BeautifulSoup, PageElement, Tag
from utils import itemize, iso_to_ap

API_ENDPOINT = "https://stanforddaily.com/wp-json/wp/v2/posts"
MINION_OPTIONS = {
    "Path": NoEscape("./MinionFontFiles/"),
    "Extension": ".ttf",
    "UprightFont": "*Regular",
    "BoldFont": "*Bold",
    "ItalicFont": "*It",
    "BoldItalicFont": "*BoldIt"
}


class Clipper:
    def __init__(self, article: str):
        # Case 1: Input is a URL with slug.
        try:
            self.slug = re.search(r"/(\d{4}/\d{2}/\d{2})/([\w-]*)/?", article).group(2)
        except AttributeError:
            # Case 2: Input is a URL with ID.
            try:
                self.slug = re.search(r"\?p=(\d+)", article).group(1)
            except AttributeError:
                # Case 3: Input is a slug.
                self.slug = article
        self.post_data = self.fetch_wordpress_post()
        self.doc = Document(font_size="large")
        self.soup = BeautifulSoup(self.post_data[0]["content"]["rendered"], "html.parser")
        self.aux_files = []

    def __del__(self):
        for filename in self.aux_files:
            os.remove(filename)

    def fetch_wordpress_post(self):
        params = {"slug": self.slug, "_embed": "true"}
        response = requests.get(API_ENDPOINT, params=params)
        if response.status_code == 200:
            return response.json()

        raise Exception(f"Failed to fetch data: {response.status_code}")

    def parse_html(self, node: PageElement | Tag) -> str:
        if node.name is None:
            return node.string.replace("$", "\\$").replace("&", "\\&").replace("#", "\\#").replace("_", "\\_").replace("%", "\\%")

        latex_content = NoEscape("")

        # Recursively parse child nodes in the DOM tree.
        for child in node.children:
            latex_content += NoEscape(self.parse_html(child))

        if node.name == "p":
            # Wrap paragraph content in LaTeX command, just in case.
            return Command("par", latex_content).dumps() + r"\\"
        elif node.name == "strong":
            # Convert <strong> to \textbf{}.
            return Command("textbf", latex_content).dumps()
        elif node.name == "a":
            # Convert <a href="..."> to \href{...}{...}.
            href = node.get("href", "")
            return Command("href", arguments=[NoEscape(href), latex_content]).dumps()
        elif node.name == "img":
            caption = node.find_next("figcaption")
            caption_text = caption.string if caption is not None else ""
            try:
                img_url = node.get("src")
            except KeyError:
                img_url = None
            fig = Figure(position="ht!")
            if img_url is None:
                return fig.dumps()
            response = requests.get(img_url)
            content = response.content

            # Save image to auxiliary file in local directory.
            aux_slug = [x for x in img_url.split("/") if len(x) > 0][-1]
            aux_path = f"{aux_slug}.jpg"
            with open(aux_path, "wb") as file:
                file.write(content)
            self.aux_files.append(aux_path)

            fig.add_image(aux_path, width="140mm")
            fig.add_caption(italic(caption_text))

            return fig.dumps()
        elif node.name == "figcaption":
            return ""  # Ignore captions, since they are handled by <img> tags.
        # TODO: Add support for other tags.
        # For headings, we can use \section{} and \subsection{} (i.e., self.doc.create(Section())).

        return latex_content

    def create_latex_document(self):
        self.doc.packages.append(Package("geometry"))
        self.doc.preamble.append(Package("parskip"))
        self.doc.preamble.append(Package("titling"))
        self.doc.preamble.append(Command("pretitle", NoEscape(r"\vspace{-4em}\begin{center}\includegraphics[width=0.5\textwidth]{logo.pdf}\end{center}\begin{flushleft}\Large\bfseries")))
        self.doc.preamble.append(Command("posttitle", NoEscape(r"\par\end{flushleft}")))
        self.doc.preamble.append(Command("preauthor", NoEscape(r"\begin{flushleft}\Large By ")))
        self.doc.preamble.append(Command("postauthor", NoEscape(r"\end{flushleft}")))
        self.doc.preamble.append(Command("predate", NoEscape(r"\begin{flushleft}")))
        self.doc.preamble.append(Command("postdate", NoEscape(r"\end{flushleft}")))
        self.doc.preamble.append(Command("usepackage", "graphicx"))
        self.doc.preamble.append(Command("pagenumbering", "gobble"))
        self.doc.packages.append(Package("xcolor"))
        self.doc.preamble.append(NoEscape(r"\definecolor{accent}{HTML}{8C1515}"))
        self.doc.preamble.append(Command("usepackage", "hyperref", options=NoEscape(r"colorlinks=true,allcolors=accent")))
        self.doc.preamble.append(Command("usepackage", "fontspec"))
        self.doc.preamble.append(Command("usepackage", "caption"))
        self.doc.preamble.append(Command("captionsetup", "labelformat=empty,width=140mm"))
        self.doc.preamble.append(Command("geometry", arguments=NoEscape(r"a4paper,total={170mm,257mm},left=20mm,top=20mm,")))
        self.doc.preamble.append(Command("pagestyle", "empty"))
        doc_title = Command("title", Command("huge", Command("textbf", NoEscape(
            BeautifulSoup(self.post_data[0]["title"]["rendered"], "html.parser").get_text()))))
        self.doc.preamble.append(doc_title)
        self.doc.preamble.append(Command("setmainfont", "MinionPro", options=MINION_OPTIONS))

        try:
            authors = [{"name": n} for n in self.post_data[0]["parsely"]["meta"]["creator"]]
            for index, author in enumerate(authors):
                author["url"] = self.post_data[0]["_embedded"]["author"][index]["link"]
        except KeyError:
            # TODO: Use post["author"] or post["coauthors"] to fill in author names.
            authors = []
        author_names = [NoEscape(Command("href", arguments=[NoEscape(a["url"]), a["name"]]).dumps()) for a
                        in authors]
        self.doc.preamble.append(Command("author", itemize(author_names)))
        self.doc.preamble.append(Command("date", iso_to_ap(self.post_data[0]["date"])))
        self.doc.append(NoEscape("\\maketitle"))
        soup = BeautifulSoup(self.post_data[0]["content"]["rendered"], "html.parser")
        parsed = self.parse_html(soup)
        # A bit of a hack, but it will do for now...
        parsed = parsed.replace("\\textbackslash{}", "\\").replace("\\{", "{").replace("\\}", "}")
        self.doc.append(NoEscape(parsed))

        return self.doc


def main():
    try:
        article_url = sys.argv[1]
    except IndexError as error:
        raise ValueError(f"Please provide article URL, ID or slug as the first positional argument.\n{error}")
    clipper = Clipper(article_url)
    doc = clipper.create_latex_document()

    # Save the document using XeLaTeX engine (otherwise, custom fonts would not work).
    doc.generate_pdf(clipper.slug, compiler="xelatex")
    if not os.path.exists("out"):
        os.mkdir("out")
    os.rename(f"{clipper.slug}.pdf", os.path.join("out", f"{clipper.slug}.pdf"))


if __name__ == "__main__":
    main()
