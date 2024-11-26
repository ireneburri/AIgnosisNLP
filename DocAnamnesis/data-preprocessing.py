import pandas as pd
import json
from csv import QUOTE_ALL

# Correctly read the CSV file while handling potential issues with quoting
df = pd.read_csv('Data/MTS-Dialog-Augmented-TrainingSet-3-FR-and-ES-3603-Pairs-final.csv',
                 quoting=QUOTE_ALL, on_bad_lines="skip", sep=';')

# Liste zum Speichern der Frage-Antwort-Paare
qa_pairs = []

# Funktion zum Erstellen von Frage-Antwort-Paaren aus einem Dialog im gewünschten Format
def extract_qa_pairs(dialogue):
    dialogue_lines = dialogue.split('\n')
    for i in range(len(dialogue_lines) - 1):
        if "Doctor:" in dialogue_lines[i] and "Patient:" in dialogue_lines[i + 1]:
            question = dialogue_lines[i].replace("Doctor: ", "").strip()
            answer = dialogue_lines[i + 1].replace("Patient: ", "").strip()
            qa_pairs.append({
                "messages": [
                    {"role": "system", "content": "You are a doctor asking relevant follow-up questions based on patient responses."},
                    {"role": "user", "content": f"Doctor: {question}"},
                    {"role": "assistant", "content": f"Patient: {answer}"}
                ]
            })
        elif "Patient:" in dialogue_lines[i] and "Doctor:" in dialogue_lines[i + 1]:
            question = dialogue_lines[i].replace("Patient: ", "").strip()
            answer = dialogue_lines[i + 1].replace("Doctor: ", "").strip()
            qa_pairs.append({
                "messages": [
                    {"role": "system", "content": "You are a doctor asking relevant follow-up questions based on patient responses."},
                    {"role": "user", "content": f"Patient: {question}"},
                    {"role": "assistant", "content": f"Doctor: {answer}"}
                ]
            })

# Dialoge durchlaufen und QA-Paare extrahieren
for index, row in df.iterrows():
    extract_qa_pairs(row['dialogue'])

# In JSONL-Datei speichern
with open('Data/qa_pairs-new.jsonl', 'w') as outfile:
    for pair in qa_pairs:
        json.dump(pair, outfile)
        outfile.write('\n')

print(f"Total QA pairs extracted: {len(qa_pairs)}")
