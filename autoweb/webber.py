import re
import os.path
import wordpress
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from paragraphs import validate_paragraphs

class Webber:
    def __init__(self, gdoc_url: str, gservice: build, wp: wordpress.API):
        self.gdoc_url = gdoc_url
        self.gservice = gservice
        self.gdoc_id = self.get_gdoc_id()
        self.gdoc_owner = self.get_gdoc_owner()
        self.document = self.gservice.documents().get(documentId=self.gdoc_id).execute()
        self.wp = wp

    def get_gdoc_id(self) -> str:
        try:
            return re.findall(r"(?<=/d/)[^/]+", self.gdoc_url)[0]
        except IndexError:
            print("Invalid Google Doc URL")

    def get_gdoc_owner(self) -> tuple:
        try:
            # Get the document metadata.
            metadata = self.gservice.files().get(fileId=self.gdoc_id, fields="owners").execute()

            # Extract the name and email address of the document owner.
            owner = metadata["owners"][0]
            name = owner.get("displayName")
            email = owner.get("emailAddress")

            return name, email
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_author_id(self):
        # Authenticate with the WordPress API.
        self.wp.auth()

        # Retrieve a list of all users from the WordPress site.
        users = self.wp.get("users").json()

        # Search for the user with the specified email address.
        for user in users:
            if user["email"] == self.gdoc_owner[1]:
                return user["id"]


    def web(self) -> dict:
        # logs in to wordpress
        # creates a new post with tokenized results of google doc body text
        # returns the post id

        # get the document body text
        body_text = self.document.get("body").get("content")
        validated_paragraphs = validate_paragraphs(body_text)

        # create a new post
        post_options = {
            "title": self.document.get("title"),
            "content": validated_paragraphs,
            "status": "draft",
            "author": self.get_author_id()
        }

        response = self.wp.put("posts", post_options)

        return response.json()