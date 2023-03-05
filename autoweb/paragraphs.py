import re
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters


def separate_paragraphs(body_text):
    # Use a regular expression to split the body text into paragraphs.
    paragraph = re.split(r"\n+", body_text)
    # Remove any leading or trailing whitespace from each paragraph.
    paragraph = [paragraph.strip() for paragraph in paragraph]
    # Remove any empty paragraphs.
    paragraph = [paragraph for paragraph in paragraph if len(paragraph) > 0]

    return paragraph


# with open("", "r") as f:  # Replace the empty string with a path.
#     text = f.read()


def string_is_sentence(s):
    if len(s) < 2:
        return False
    if s[-1] not in {".", "!", "?", "\"", "\u201d"}:
        return False
    if re.findall(r"excerpt:.+", s.lower()):
        return False

    return True


config = PunktParameters()
config.abbrev_types = {
    "jan", "feb", "aug", "sept",
    "oct", "nov", "calif", "ph.d",
    "sen", "sens", "j.d", "dr",
    "u.s"
}
tokenizer = PunktSentenceTokenizer(config)


def validate_paragraphs(paragraphs):
    result = []
    for paragraph in separate_paragraphs(paragraphs):
        tokens = tokenizer.tokenize(paragraph)
        sentences = []
        for t in tokens:
            if string_is_sentence(t.strip()):
                # print("SENTENCE\t" + t)
                sentences.append(t)
                # yield t
        if len(sentences) > 0:
            # print("PARAGRAPH\t" + "\n".join(sentences))
            result.append(sentences)
    return result


# for para in validate_paragraphs(text):
#     print(para)