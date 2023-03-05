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

# The ID of a sample document.
DOCUMENT_ID = "1_fKL7KMJ6wY_DfWUMWT0AGE9SPMXU-oWLf3nbYLI23A"

CLIENT_KEY, CLIENT_SECRET = load_env()

def generate_html(doc_info):
    html = ""

    for item in doc_info:
        if "sectionBreak" in item:
            html += "<hr>"
        elif "paragraph" in item:
            content = ""
            for element in item["paragraph"]["elements"]:
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

def fetch_doc():
    # Basic Google Doc retrieval adapted from https://developers.google.com/docs/api/quickstart/python.
    creds = None
    # The file token.json stores the user"s access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("docs", "v1", credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()

        print("The title of the document is: {}".format(document.get("title")))
        # extract text runs
        content = document.get("body").get("content")
        text_runs = []
        for i in content:
            if i.get("paragraph"):
                text_runs.append(i.get("paragraph").get("elements"))
        # extract text
        text = []
        for text_run in text_runs:
            for t in text_run:
                if t.get("textRun"):
                    text.append(t.get("textRun").get("content").strip())

        ghc = generate_html(content)

        ghc = re.sub(r"<p>\s*</p>", "", ghc)
        ghc = ghc.replace("<hr>", "")
        final_result = ""
        for line in ghc.split("\n"):
            ii = line.replace("<p>", "").replace("</p>", "")
            if paragraphs.string_is_sentence(ii.strip()):
                final_result += f"<!-- wp:paragraph -->\n<p>{ii}</p>\n<!-- /wp:paragraph -->\n"

        return final_result
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    print(fetch_doc())