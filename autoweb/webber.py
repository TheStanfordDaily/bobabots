import re
import json
import requests
from requests.auth import HTTPBasicAuth
from autoweb.quickstart import fetch_doc
from utils import load_env
from quickstart import generate_html, block_format
from googleapiclient.errors import HttpError

BASE_URL = "https://stanforddaily.com"
CLIENT_KEY, CLIENT_SECRET = load_env()


class Webber:
    def __init__(self, gdoc_url: str):
        self.gdoc_url = gdoc_url
        self.gdoc_id = self.get_gdoc_id()
        self.gdoc = fetch_doc(self.gdoc_id)
        self.gdoc_title = self.gdoc.get("title")

        # Extract text runs from body of document.
        content = self.gdoc.get("body").get("content")
        text_elements = []
        text_runs = []

        for element in content:
            if element.get("paragraph"):
                text_elements.append(element.get("paragraph").get("elements"))

        for element in text_elements:
            for t in element:
                if t.get("textRun"):
                    text_runs.append(t.get("textRun").get("content").strip())

        content_html = generate_html(content)
        self.blocks = block_format(content_html)

    def get_gdoc_id(self) -> str:
        try:
            return re.findall(r"(?<=/d/)[^/]+", self.gdoc_url)[0]
        except IndexError:
            print("Invalid Google Doc URL")

    def get_gdoc_owner(self) -> tuple:
        try:
            # Get the document metadata.
            metadata = self.gdoc.get("metadata")

            # Extract the name and email address of the document owner.
            owner = metadata["owners"][0]
            name = owner.get("displayName")
            email = owner.get("emailAddress")

            return name, email
        except HttpError as error:
            print(f"An error occurred: {error}")

    # TODO: Write function to get author ID from email address of Google Doc owner.

    def web(self) -> dict:
        endpoint = BASE_URL + "/wp-json/wp/v2/posts"
        wp_auth = HTTPBasicAuth(CLIENT_KEY, CLIENT_SECRET)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        post_options = {
            "title": self.gdoc_title + " [autowebbed]",
            "content": self.blocks,
            "status": "draft"
        }

        response = requests.request("POST", endpoint, data=json.dumps(post_options), headers=headers, auth=wp_auth)

        return response.json()


if __name__ == "__main__":
    w = Webber("https://docs.google.com/document/d/1_fKL7KMJ6wY_DfWUMWT0AGE9SPMXU-oWLf3nbYLI23A/edit")
    print(w.web())
