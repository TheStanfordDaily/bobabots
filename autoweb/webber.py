import re
import json
import requests
from requests.auth import HTTPBasicAuth
from autoweb.quickstart import fetch_doc
from utils import load_env
from quickstart import generate_html, block_format
from googleapiclient.errors import HttpError

BASE_URL = "https://stanforddaily.com"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
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
        # TODO: Get email address of owner of Google Doc (heuristic for author of article).
        pass

    def get_wp_user(self) -> int:
        try:
            email = self.get_gdoc_owner()[0]
        except TypeError:
            raise ValueError("No email address found for Google Doc owner")

        response = requests.get(BASE_URL + "users?search=" + email)

        if response.status_code == 200:
            users = response.json()
            if len(users) > 0:
                return users[0]["id"]  # Get the ID of the first user found.

        raise ValueError(f"Request failed with status code {response.status_code}")

    def web(self) -> dict:
        endpoint = BASE_URL + "/wp-json/wp/v2/posts"
        wp_auth = HTTPBasicAuth(CLIENT_KEY, CLIENT_SECRET)
        post_options = {
            "title": self.gdoc_title + " [autowebbed]",
            "content": self.blocks,
            "status": "draft"
        }

        try:
            wp_user = self.get_wp_user()
        except ValueError:
            wp_user = None

        if wp_user is not None:
            post_options["author"] = wp_user

        response = requests.request("POST", endpoint, data=json.dumps(post_options), headers=HEADERS, auth=wp_auth)

        return response.json()


if __name__ == "__main__":
    w = Webber("https://docs.google.com/document/d/1_fKL7KMJ6wY_DfWUMWT0AGE9SPMXU-oWLf3nbYLI23A/edit")
    print(w.web())
