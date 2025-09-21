from faker import Faker
import spacy

fake = Faker()
nlp = spacy.load("en_core_web_sm")

def is_aadhaar(text):
    text = text.replace(" ", "")
    return text.isdigit() and len(text) == 12

def detect_pii(text):
    doc = nlp(text)
    pii = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE"]:
            pii.append((ent.text, "NAME" if ent.label_ == "PERSON" else "ADDRESS"))
        elif ent.label_ == "DATE":
            pii.append((ent.text, "DATE"))
    digits = ''.join(c for c in text if c.isdigit())
    if len(digits) == 10:
        pii.append((text, "PHONE"))
    if is_aadhaar(text):
        pii.append((text, "AADHAAR"))
    return pii

def generate_dummy(pii_type):
    if pii_type == "NAME":
        return fake.name()
    elif pii_type == "ADDRESS":
        return fake.address().replace('\n', ', ')
    elif pii_type == "PHONE":
        return fake.numerify('##########')
    elif pii_type == "DATE":
        return fake.date(pattern='%d-%m-%Y')
    elif pii_type == "AADHAAR":
        return fake.numerify('#### #### ####')
    return "[Redacted]"