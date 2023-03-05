import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from autoweb import paragraphs
from utils import load_env

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
CLIENT_KEY, CLIENT_SECRET = load_env()


def generate_html(doc_info) -> str:
    html = ""

    for item in doc_info:
        if "sectionBreak" in item:
            html += "<hr>"
        elif "paragraph" in item:
            content = ""
            for element in item["paragraph"]["elements"]:
                # TODO: Also check for long spans of newlines or other related whitespace.
                if "textRun" not in element:
                    return html
                text = element["textRun"]["content"]
                style = element["textRun"]["textStyle"]

                if "link" in style:
                    href = style["link"]["url"]
                    content += f'<a href="{href}">{text}</a>'
                elif "italic" in style:
                    content += f"<em>{text}</em>"
                elif "bold" in style:
                    content += f"<strong>{text}</strong>"
                else:
                    content += text

            html += f"<p>{content}</p>"

    return html


def block_format(s) -> str:
    block = re.sub(r"<p>\s*</p>", "", s)
    block = block.replace("<hr>", "")
    block_formatted = ""
    for line in block.split("\n"):
        element = line.replace("<p>", "").replace("</p>", "")
        if paragraphs.string_is_sentence(element.strip()):
            block_formatted += f"<!-- wp:paragraph -->\n<p>{element}</p>\n<!-- /wp:paragraph -->\n"

    return block_formatted


def fetch_doc(doc_id) -> dict:
    # Basic Google Doc retrieval adapted from https://developers.google.com/docs/api/quickstart/python.
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("../token.json"):
        creds = Credentials.from_authorized_user_file(os.path.join(os.path.dirname(__file__), "..", "token.json"), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(os.path.dirname(__file__), "..", "credentials.json"), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(os.path.dirname(__file__), "..", "token.json"), "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=doc_id).execute()

        return document
    except HttpError as error:
        print(f"An error occurred: {error}")
