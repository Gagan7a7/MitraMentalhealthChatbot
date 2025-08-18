import pandas as pd
import json
from fuzzywuzzy import process

# Reference list of valid course names (expand as needed)
VALID_COURSES = [
    "Engineering", "BIT", "Law", "Mathematics", "Psychology", "Accounting", "Banking Studies", "Business Administration", "Biomedical Science", "Human Resources", "Islamic Education", "Pendidikan Islam", "Marine Science", "KOE", "KENMS", "ENM", "CTS", "IT", "Econs", "Usuluddin", "Radiography", "Communication", "Diploma Nursing", "Fiqh", "Fiqh Fatwa", "Human Sciences"
]

def correct_course_name(course):
    if pd.isnull(course):
        return "Unknown"
    match, score = process.extractOne(str(course).strip().title(), VALID_COURSES)
    return match if score > 80 else course.strip().title()

def clean_student_data(input_path, output_path):
    df = pd.read_csv(input_path)
    # Drop rows with missing age, course, or mental health columns
    df = df.dropna(subset=["Age", "What is your course?", "Do you have Depression?", "Do you have Anxiety?", "Do you have Panic attack?"])
    # Standardize year and course names, correct spelling
    df["Your current year of Study"] = df["Your current year of Study"].str.lower().str.replace("year ", "").str.replace(" ", "")
    df["What is your course?"] = df["What is your course?"].apply(correct_course_name)
    # Save cleaned data
    df.to_csv(output_path, index=False)



import re
def fix_encoding(text):
    if pd.isnull(text):
        return text
    replacements = {
        "â€™": "'",
        "â€“": "-",
        "â€”": "-",
        "â€œ": '"',
        "â€�": '"',
        "â€¦": "...",
        "Â": "",
        "Ã": "",
        "€™": "'",
        "€": "-",
        "™": "'",
        "œ": "oe",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "-",
        "": "-",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
        "": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

def clean_faq(input_path, output_path):
    df = pd.read_csv(input_path)
    # Drop duplicates and rows with missing questions/answers
    df = df.drop_duplicates(subset=["Questions"]).dropna(subset=["Questions", "Answers"])
    # Remove leading/trailing whitespace, fix capitalization, and encoding
    df["Questions"] = df["Questions"].apply(lambda x: fix_encoding(str(x).strip().capitalize()))
    df["Answers"] = df["Answers"].apply(lambda x: fix_encoding(str(x).strip()))
    df.to_csv(output_path, index=False)

def clean_intents(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Remove duplicate intents by tag
    seen = set()
    cleaned_intents = []
    for intent in data["intents"]:
        if intent["tag"] not in seen:
            seen.add(intent["tag"])
            # Remove duplicate patterns and responses, fix capitalization
            intent["patterns"] = list(set([p.strip().capitalize() for p in intent["patterns"] if p]))
            intent["responses"] = list(set([r.strip() for r in intent["responses"] if r]))
            cleaned_intents.append(intent)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"intents": cleaned_intents}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    clean_student_data("data/Student Mental health.csv", "data/Student_Mental_health_cleaned.csv")
    clean_faq("data/Mental_Health_FAQ.csv", "data/Mental_Health_FAQ_cleaned.csv")
    clean_intents("data/intents1.json", "data/intents1_cleaned.json")
