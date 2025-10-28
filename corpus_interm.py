import os
import re
import ast
import pandas as pd
import xml.etree.ElementTree as ET

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def parse_span(span_str):
    """Extract numeric start and end positions from a string like '123-456'."""
    nums = re.findall(r'\d+', span_str)
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    return 0, 0

def spans_overlap(a_start, a_end, b_start, b_end):
    """Check if two text spans overlap."""
    return not (b_end < a_start or b_start > a_end)

def find_section(sent_start, sent_end, sections):
    """Find the section title corresponding to a sentence span."""
    for sec in sections:
        if spans_overlap(sec['start'], sec['end'], sent_start, sent_end):
            for sub in sec['subsections']:
                if spans_overlap(sub['start'], sub['end'], sent_start, sent_end):
                    return sub['title']
            return sec['title']
    return ""

def extract_sections(sec):
    """Récupère récursivement toutes les sections et sous-sections."""
    title = sec.attrib.get("title", "").strip()
    start, end = parse_span(sec.attrib.get("textSpan", "0-0"))
    section_info = {"title": title, "start": start, "end": end, "subsections": []}
    for sub in sec.findall("section"):
        section_info["subsections"].append(extract_sections(sub))
    return section_info

def collect_all_titles(sections):
    """Retourne une liste plate de tous les titres de section (tous niveaux)."""
    titles = []
    for sec in sections:
        if sec['title']:
            titles.append(sec['title'].lower())
        if sec['subsections']:
            titles.extend(collect_all_titles(sec['subsections']))
    return titles

# -------------------------
# CONFIGURATION
# -------------------------
XML_FOLDER = "/QA_CONSORT/CONSORT-TM_stats/item_distribution/50_XML"
GOLD_FILE = "/QA_CONSORT/AQG/mistral/Gold.xlsx"   # gold questions
OUTPUT_FILE = "corpus_QA.xlsx"      # final dataset

# -------------------------
# LOAD GOLD QUESTIONS
# -------------------------
gold_df = pd.read_excel(GOLD_FILE, dtype=str).fillna('')
questions_map = {
    str(item).strip(): question 
    for item, question in zip(gold_df["Item_No"], gold_df["Gold_Question"])
}

# -------------------------
# MAIN SCRIPT
# -------------------------
results = []

for filename in os.listdir(XML_FOLDER):
    if not filename.endswith(".xml"):
        continue
    pmcid = filename.replace(".xml", "")
    xml_path = os.path.join(XML_FOLDER, filename)

    try:
        root = ET.parse(xml_path).getroot()
    except Exception as e:
        print(f"[ERROR] Could not parse {xml_path}: {e}")
        continue

    # --- Extract sections recursively
    sections = []
    for sec in root.findall(".//section"):
        sections.append(extract_sections(sec))

    # --- Collect all titles for filtering
    all_titles = collect_all_titles(sections)

    # --- Extract sentences and labels
    sentences = []
    for s in root.findall(".//sentence"):
        sid = s.attrib.get("id", "").strip()
        text = (s.findtext("text") or "").strip()
        if not text:
            continue

        start, end = parse_span(s.attrib.get("charOffset", "0-0"))
        sec_title = find_section(start, end, sections)

        # --- Labels
        raw_label = s.attrib.get("selection", "").strip()
        if raw_label:
            lbl_list = [lbl.strip() for lbl in raw_label.split(",") if lbl.strip()]
        else:
            lbl_list = ["0"]

        # --- Check if it is a section title (any depth)
        is_section_title = text.lower() in all_titles
        if is_section_title and "1a" not in lbl_list:
            # Skip section/subsection titles
            continue

        # Store real sentence
        sentences.append({
            "id": sid,
            "text": text,
            "section": sec_title,
            "labels": lbl_list
        })

    # --- Group sentences into 3–5
    i = 0
    while i < len(sentences):
        group_sentences = sentences[i:i+5]
        if len(group_sentences) < 3:
            break

        # Build context with section titles
        context_text = ""
        last_section = None
        for s in group_sentences:
            # on ignore le titre de section, sauf éventuellement item 1a
            context_text += s['text'] + " "

        # Labels per phrase
        labels_per_phrase = [s['labels'] for s in group_sentences]

        # Build CONSORT_Dict and Answers
        consort_dict = {}
        answers_dict = {}
        for idx, (labs, s) in enumerate(zip(labels_per_phrase, group_sentences)):
            if not labs:
                continue

            # Key: (index, tuple of labels) if multiple, else (index, single label)
            key = (idx, tuple(labs)) if len(labs) > 1 else (idx, labs[0])

            # Questions
            questions = tuple(questions_map.get(lab, "[Question not found]") for lab in labs)
            questions_val = questions if len(questions) > 1 else questions[0]
            consort_dict[key] = questions_val

            # Answers = actual sentence text
            answers_dict[key] = s['text']

        results.append({
            "PMCID": pmcid,
            "Sentence_IDs": ", ".join([s['id'] for s in group_sentences]),
            "Context": context_text.strip(),
            "CONSORT_Labels": ", ".join([str(s['labels']) for s in group_sentences]),
            "CONSORT_Dict": consort_dict,
            "Answers": answers_dict
        })

        i += len(group_sentences)

# -------------------------
# SAVE FINAL DATASET
# -------------------------
out_df = pd.DataFrame(results)
out_df.to_excel(OUTPUT_FILE, index=False)
print(f"Final dataset generated: {OUTPUT_FILE} ({len(results)} contexts).")
