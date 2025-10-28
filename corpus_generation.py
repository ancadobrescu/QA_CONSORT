import pandas as pd
import json
import ast
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

# -------------------------
# CONFIGURATION
# -------------------------
INPUT_FILE = "corpus_QA.xlsx"
GOLD_FILE = "/QA_CONSORT/AQG/mistral/Gold.xlsx"
OUTPUT_JSON = "corpus_QA.json"

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel(INPUT_FILE, dtype=str).fillna('')

print("Columns in input file:", df.columns.tolist())  # Vérifie les colonnes

def parse_dict_column(s):
    if pd.isna(s) or s == "":
        return {}
    try:
        return ast.literal_eval(s)
    except:
        return {}

df["CONSORT_Dict"] = df.get("CONSORT_Dict", pd.Series([{}]*len(df))).apply(parse_dict_column)
df["Answers"] = df.get("Answers", pd.Series([{}]*len(df))).apply(parse_dict_column)

# -------------------------
# LOAD GOLD QUESTIONS
# -------------------------
df_gold = pd.read_excel(GOLD_FILE, dtype=str).fillna('')
all_gold_questions = df_gold["Gold_Question"].tolist()
gold_question_to_item = dict(zip(df_gold["Gold_Question"], df_gold["Item_No"]))

# -------------------------
# INITIALIZE COUNTERS
# -------------------------
num_random_questions = 0
item_distribution = {}
num_normal_questions = 0
total_questions = 0
item_distribution_all = {}

# -------------------------
# UTIL FUNCTIONS
# -------------------------
def get_answer_positions(context, answer_text):
    """Retourne start et end de la réponse dans le contexte"""
    if not answer_text:
        return 0, 0
    start = context.find(answer_text)
    if start == -1:
        return 0, 0
    end = start + len(answer_text)
    return start, end

# -------------------------
# BUILD SQuAD-LIKE JSON
# -------------------------
squad_data = {"data": []}

for idx, row in tqdm(df.iterrows(), total=len(df)):
    pmcid = row["PMCID"]
    context_text = row["Context"]
    consort_dict = row["CONSORT_Dict"]
    answers_dict = df["Answers"].iloc[idx]

    qas_list = []

    # --- Parcours des questions ---
    for key, question in consort_dict.items():
        question_is_missing = (isinstance(question, str) and question.strip() == "[Question not found]") or str(key[1]) == "0"

        if question_is_missing:
            continue

        else:
            answer_text = answers_dict.get(key, None)
            if isinstance(question, (list, tuple)):
                question_list = question
            else:
                question_list = [question]

            if not answer_text:
                answer_list = [{"text": "", "answer_start": 0, "answer_end": 0}]
            else:
                start, end = get_answer_positions(context_text, answer_text)
                answer_list = [{"text": answer_text, "answer_start": start, "answer_end": end}]

            # Comptage des questions normales et distribution par item
            num_normal_questions += 1
            item_key_normal = "_".join(key[1]) if isinstance(key[1], tuple) else str(key[1])
            item_distribution_all[item_key_normal] = item_distribution_all.get(item_key_normal, 0) + 1

        for i, q in enumerate(question_list):
            qid = f"{pmcid}_{key[0]}_{'_'.join(key[1])}" if isinstance(key[1], tuple) else f"{pmcid}_{key[0]}_{key[1]}"
            if len(question_list) > 1:
                qid += f"_q{i}"

            item_key = "_".join(key[1]) if isinstance(key[1], tuple) else str(key[1])

            qas_list.append({
                "id": qid,
                "question": q,
                "answers": answer_list,
                "sub_answers": [],
                "item_key": item_key
            })

    # --- Fusionner toutes les réponses par item_key ---
    qas_by_item = {}
    for qa in qas_list:
        if qa["item_key"] in qas_by_item:
            qas_by_item[qa["item_key"]]["answers"].extend(qa["answers"])
        else:
            qas_by_item[qa["item_key"]] = {
                "id": qa["id"],
                "question": qa["question"],
                "answers": qa["answers"].copy(),
                "sub_answers": []
            }

    # --- Construire sub_answers et concaténer seulement les QAs consécutifs avec le même item_key ET la même question ---
    merged_qas = []

    if qas_list:
        current_item_key = qas_list[0]["item_key"]
        current_question = qas_list[0]["question"]
        current_qid = qas_list[0]["id"]
        current_answers = qas_list[0]["answers"].copy()

        for qa in qas_list[1:]:
            # Fusion seulement si item_key ET question identiques
            if qa["item_key"] == current_item_key and qa["question"] == current_question:
                current_answers.extend(qa["answers"])
            else:
                # Dédupliquer les réponses
                unique_answers = []
                seen = set()
                for a in current_answers:
                    key = (a["text"], a["answer_start"], a["answer_end"])
                    if key not in seen and a["text"].strip():
                        seen.add(key)
                        unique_answers.append(a)

                if len(unique_answers) > 1:
                    sub_answers = unique_answers
                    merged_text = " ".join([a["text"] for a in unique_answers])
                    start, end = get_answer_positions(context_text, merged_text)
                    answers = [{"text": merged_text, "answer_start": start, "answer_end": end}]
                else:
                    sub_answers = []
                    answers = unique_answers

                merged_qas.append({
                    "id": current_qid,
                    "question": current_question,
                    "answers": answers,
                    "sub_answers": sub_answers,
                    "item_key": current_item_key
                })

                # Nouveau bloc
                current_item_key = qa["item_key"]
                current_question = qa["question"]
                current_qid = qa["id"]
                current_answers = qa["answers"].copy()

        # Sauvegarde du dernier bloc
        unique_answers = []
        seen = set()
        for a in current_answers:
            key = (a["text"], a["answer_start"], a["answer_end"])
            if key not in seen and a["text"].strip():
                seen.add(key)
                unique_answers.append(a)

        if len(unique_answers) > 1:
            sub_answers = unique_answers
            merged_text = " ".join([a["text"] for a in unique_answers])
            start, end = get_answer_positions(context_text, merged_text)
            answers = [{"text": merged_text, "answer_start": start, "answer_end": end}]
        else:
            sub_answers = []
            answers = unique_answers

        merged_qas.append({
            "id": current_qid,
            "question": current_question,
            "answers": answers,
            "sub_answers": sub_answers,
            "item_key": current_item_key
        })

    # --- Ajouter les QAs sans réponse ---
    merged_qas += [qa for qa in qas_list if qa["answers"][0]["text"] == "" and qa["item_key"] not in qas_by_item]

    # --- Ajouter le document courant ---
    squad_data["data"].append({
        "doc": pmcid,
        "context": context_text,
        "context_start": 0,
        "context_end": len(context_text),
        "qas": merged_qas
    })


# -------------------------
# SAVE JSON
# -------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(squad_data, f, ensure_ascii=False, indent=2)

# -------------------------
# PRINT STATISTICS
# -------------------------

print(f"Total normal questions: {num_normal_questions}")

print("Distribution of items for all normal questions:")
for item, count in item_distribution_all.items():
    print(f"{item}: {count}")

# --- Distribution ordonnée par Gold ---
gold_item_order = df_gold["Item_No"].tolist()
counts_ordered_all = [item_distribution_all.get(item, 0) for item in gold_item_order]

print("Distribution of items for all normal questions (ordered by Gold file):")
for item, count in zip(gold_item_order, counts_ordered_all):
    print(f"{item}: {count}")