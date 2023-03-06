import os
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from autoweb import paragraphs
from utils import load_env
from pprint import pprint

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/documents.readonly", "https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_KEY, CLIENT_SECRET = load_env()
NEWLINE_THRESHOLD = 4


def generate_html(doc_info) -> str:
    html = ""
    # Check for long spans of newlines or other related whitespace.
    newline_ticker = 0

    for item in doc_info:
        if "sectionBreak" in item:
            html += "<hr>"
        elif "paragraph" in item:
            content = ""
            for element in item["paragraph"]["elements"]:
                # Check for a page break.
                if "textRun" not in element:
                    return html
                text = element["textRun"]["content"]
                style = element["textRun"]["textStyle"]
                if text == "\n":
                    newline_ticker += 1
                    # Check for a long sequence of newlines.
                    if newline_ticker > NEWLINE_THRESHOLD:
                        return html
                else:
                    newline_ticker = 0

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


def load_creds() -> Credentials:
    # Basic Google Doc retrieval adapted from https://developers.google.com/docs/api/quickstart/python.
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "token.json")):
        creds = Credentials.from_authorized_user_file(os.path.join(os.path.dirname(__file__), "..", "token.json"),
                                                      SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(os.path.dirname(__file__), "..", "credentials.json"), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open(os.path.join(os.path.dirname(__file__), "..", "token.json"), "w") as token:
            token.write(creds.to_json())

    return creds


def fetch_doc(doc_id) -> dict:
    try:
        service = build("docs", "v1", credentials=load_creds())
        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=doc_id).execute()

        return document
    except HttpError as error:
        raise RuntimeError(f"Error fetching Google Doc: {error}")


def fetch_inbox() -> list:
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=load_creds())
        messages = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        message_ids = [x["id"] for x in messages["messages"]]
        message_list = []
        for message_id in message_ids[:10]:
            message = service.users().messages().get(userId="me", id=message_id).execute()
            headers = message["payload"]["headers"]
            senders = [x["value"] for x in headers]
            if any("@docs-share.google.com>" in s for s in senders):
                # TODO: Add a condition to check whether this is a new message (i.e., not already in the database or a certain amount of time has passed)
                message_list.append(message)

        return message_list
    except HttpError as error:
        raise RuntimeError(f"Error fetching inbox: {error}")

if __name__ == "__main__":
    # pretty print
    inbox_list = fetch_inbox()
    pprint(inbox_list)
    print(len(inbox_list))
