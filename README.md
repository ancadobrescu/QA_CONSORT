# CONSORT-TM: From Sentence Classification to Question Answering

## Project Overview

This project explores whether transforming a **sentence classification task** into a **question answering (QA) task** can improve the identification of **CONSORT items** in clinical trial reports.  

The work builds upon the **CONSORT-TM corpus**, which contains **sentence-level annotations** corresponding to CONSORT checklist items. To adapt this resource for QA, the corpus has been **automatically transformed** into a QA-style dataset, where:  
- **Questions** are generated from the CONSORT items, and  
- **Answers** correspond to the annotated sentences in the original corpus.

This approach allows evaluating whether reframing the problem as QA provides better contextual understanding and performance in identifying CONSORT-related information.

## Background

CONSORT (Consolidated Standards of Reporting Trials) is a set of guidelines that help ensure transparent reporting of randomized clinical trials.

CONSORT-TM is a manually annotated corpus mapping sentences to specific CONSORT checklist items.

This project transforms CONSORT-TM into a QA-oriented dataset to enable modern QA architectures to reason over trial reports.

## Project Structure

The repository contains the following main directories and files:

### **AQG/** 
Automatic Question Generation scripts and resources  
  - **mistral/**  
    - `CONSORT_items.xlsx` – The CONSORT-style checklist.  
    - `Gold.xlsx` – The CONSORT checklist with manually constructed questions based on CONSORT items.  
    - `mistral.py` – Automatically generates clear, grammatically correct questions from CONSORT checklist items using a locally loaded Mistral language model at different temperature settings. Results and generation times are saved in Excel files.  
    - `prompt_stability.py` – Aggregates and visualizes the stability of QA question generation metrics across multiple runs and temperatures by reading per-run Excel results, computing averages, and generating plots.  
      - **Base folder used:** `Evaluation_Results/` (contains input Excel files from `mistral.py`, named like `scores_temp_<temperature>_run_<run_idx>.xlsx`)  
      - **Folder created:** `Evaluation_Results/Plots/` (contains plots visualizing metric stability across runs and temperatures)  
      - **Files generated:**  
        - `summary_stability.xlsx`  
          - **Sheet "Global_Summary"** – Contains average metrics per temperature (`BERTScore_F1`, `ROUGE-L_F1`, `BLEU`, `Exact_Match_Ratio`)  
          - **Sheet "File_Averages"** – Contains metrics for each input file, with temperature and run info  
        - **Plots per temperature:** `combined_metrics_temp_<temperature>.png` – Line plots showing all metrics across runs for a given temperature, with global average lines  
        - **Global plots:**  
          - `<metric>_all_temps.png` – Line plots of each metric across all runs with temperature labels  
          - `<metric>_avg_per_temperature.png` – Line plot of the average metric per temperature  
          - `combined_metrics_per_temperature.png` – Bar plot combining all metrics per temperature  
    - `scores.py` – Evaluates the quality of generated QA questions against the gold standard by computing BERTScore F1, ROUGE-L F1, BLEU, and exact match metrics, while handling trailing averages or empty lines.  
      - **Base input folder:** `Generated_Questions/` (contains subfolders per temperature, e.g., `temp_<temperature>/`, with Excel files produced by `mistral.py`)  
      - **Base output folder created:** `Evaluation_Results/` (stores evaluation Excel files named like `scores_<temp_dir>_<gen_file>.xlsx`)  
      - **Each evaluation Excel file contains:**  
        - `Item No` – Item numbers  
        - `Checklist item` – Original CONSORT checklist item  
        - `Gold Question` – Reference question from the gold standard  
        - `Generated question` – Normalized generated question  
        - `BERTScore_F1` – BERTScore F1 between generated and gold  
        - `ROUGE-L_F1` – ROUGE-L F1  
        - `BLEU` – BLEU score  
        - `Match` – Exact match (Yes/No)  
        - **Last row:** `"=== AVERAGE ==="` showing averages for all metrics and total exact matches  

    - `Generated_Questions/` – Contains one subfolder per temperature setting, e.g., `temp_1e-5/`, `temp_0.5/`, `temp_1/`.  
    - **Subfolders (`temp_<temperature>/`)**:  
        - Contains Excel files named like `QG_mistral_temp_<temperature>_run_<run_idx>.xlsx`  
        - Each Excel file contains:  
        - Columns from the original `CONSORT_items.xlsx`  
        - New columns for each temperature:  
            - `QG_temp_<temperature>` – Generated questions  
            - `GenTime_temp_<temperature>` – Time taken to generate each question  
        - **Last row:** average generation time for that temperature run  

    - `Evaluation_Results/` – Stores all evaluation files (`scores_*.xlsx`) and plots generated by `prompt_stability.py`.

 - **biomistral/**
        - `Generated_Questions/` – Contains one subfolder per temperature setting, e.g., `temp_1e-5/`, `temp_0.5/`, `temp_1/`, for questions generated using the biomistral model.

### **CONSORT-TM_stats/** 
Statistics and analyses on the original CONSORT-TM corpus  
  - **complexity/** – contains analyses related to the complexity of the corpus (e.g., sentence lengths, vocabulary statistics).  
    - **Stats_Complexity.ipynb** – Notebook analyzing complexity metrics across questions by type.  
        - **Functionality:**  
        - Loads `complexity_by_question_type.xlsx`, which contains per-question complexity metrics computed earlier.  
        - Generates bar plots for multiple metrics by question type, including:  
            - `flesch_reading_ease`  
            - `flesch_kincaid_grade`  
            - `gunning_fog`  
            - `avg_sentence_length`  
            - `word_count`  
            - `bert_token_count`  
        - Maps numeric scores to readability categories or school/reading levels for easier interpretation:  
            - Flesch Reading Ease → difficulty categories (Very Easy → Very Confusing)  
            - Flesch-Kincaid Grade → school grade levels  
            - Gunning Fog Index → approximate reading grade level  
        - Adds annotations above bars for exact values.  
        - Uses custom color palettes for readability/difficulty categories.  
        - **Outputs (saved in `plots_complexity/`):**  
        - `<metric>_by_question_type.png` – Bar plots for each metric by question type.  
        - `Flesch_Reading_Score_by_question_type.png` – Flesch Reading Ease with difficulty-based coloring.  
        - `Flesch_Kincaid_Grade_by_question_type.png` – Flesch-Kincaid Grade with school-level coloring.  
        - `Gunning_Fog_by_question_type.png` – Gunning Fog Index with reading-level coloring.  
       
    - **Complexity.py** – Script computing complexity metrics for BioBERT-predicted answers per CONSORT item.  
        - **Functionality:**  
        - Loads `biobert_predictions_enriched.xlsx`, containing predicted answers with multiple CONSORT labels per row.  
        - Explodes rows with multiple labels so that each row corresponds to a single label.  
        - Computes complexity metrics for each answer:  
            - `flesch_reading_ease`  
            - `flesch_kincaid_grade`  
            - `gunning_fog`  
            - `avg_sentence_length`  
            - `word_count`  
            - `bert_token_count` (using `BertTokenizer`)  
        - Aggregates metrics to compute mean complexity per question type (`Consort_True_Labels_list`).  
        - **Outputs:**  
        - `biobert_predictions_with_complexity_per_item.xlsx` → one row per label with computed complexity metrics.  
        - `complexity_by_question_type.xlsx` → average complexity metrics per question type (used as input for `Stats_Complexity.ipynb` plots).  

  - **item_distribution/**  
    - **50_XML/** – 50 PMC articles in XML format, annotated at the sentence level with CONSORT items (the original CONSORT-TM corpus).  
    - **section_pres.py** – Script that extracts and counts CONSORT items per article section. It reads all XML files in `50_XML/`, normalizes section titles, maps equivalent section names, and assigns items to sections based on character offsets.  
      - **Output:** `items_per_section_docs_with_equivalents.xlsx`  
        - Each row corresponds to a CONSORT item.  
        - Columns include:  
          - `item` – the item name  
          - One column per main section (Title, Abstract, Introduction, Methods, Results, Discussion, Conclusions, Back Matter) listing the PMCIDs of articles containing the item.  
          - One column per section with the count of documents containing the item (`<section>_count`).  
    - **Collapsed_sections.xlsx** – Mapping of equivalent or composed sections to their standardized section names.  
      - Columns include:  
        - `Composing_sections` – original section titles found in the XML files.  
        - `Collapsed_section` – standardized section title after collapsing equivalents.  
        - `Documents` – PMCIDs of documents where the section appears.  
        - `Number of documents where the section appears` – total count of documents per collapsed section.  
    - **Plots_metricsQA_folds.ipynb** – Notebook that reads `items_per_section_docs_with_equivalents.xlsx` and visualizes the distribution of items across sections.  
      - **Analysis and plots:**  
        - Prints combinations of sections where each item appears and counts of documents per combination.  
        - Generates a grouped bar plot (`plots/all_items_sections_grouped_separated_compact.png`) showing for each item the number of documents in each main section, with section colors and vertical separators between items.  
      - **Output:**  
        - `plots/all_items_sections_grouped_separated_compact.png` – compact grouped bar plot with document counts per section for each CONSORT item.  
    - **Complexity_tok_section.py** – Script that analyzes token counts and text complexity per section and per sentence in the 50 PMC XML articles.  
      - **Functionality:**  
        - Parses XML files in `50_XML/` and identifies sections and subsections.  
        - Tokenizes text using the BioBERT tokenizer.  
        - Computes tokens per sentence, tokens per section, and total tokens per document.  
        - Computes text complexity metrics per section using `textstat` (Flesch Reading Ease, Flesch-Kincaid grade, Gunning-Fog index, average sentence length, word count, and BERT token count).  
      - **Outputs (saved in `outputs_tokens/`):**  
        - `tokens_per_sentence.xlsx` → each sentence with PMC ID, section, number of tokens, and text.  
        - `tokens_per_document.xlsx` → total tokens per document.  
        - `mean_tokens_per_section.xlsx` → mean, min, max, and document count of tokens per section.  
        - `complexity_per_section.xlsx` → detailed complexity metrics per section per document.  
        - `complexity_average_by_section.xlsx` → average complexity metrics per section across all documents.  
        - `global_means.xlsx` → global averages of tokens per document, per sentence, and per section.  

### **corpus_QA/** 
Scripts and files for constructing the QA corpus from the CONSORT-TM XML files.  
  - **corpus_interm.py** – Script that generates a QA-style dataset (intermediate excel file) from the 50 PMC XML articles in `item_distribution/50_XML/`.  
     **Functionality:**  
      - Loads the 50 PMC XML articles annotated with CONSORT items.  
      - Loads the gold questions from `Gold.xlsx` mapping CONSORT items to their corresponding questions.  
      - Extracts sections and subsections recursively for each article.  
      - Extracts sentences, their character offsets, and assigned CONSORT item labels.  
      - Skips section/subsection titles unless they contain item `1a`.  
      - Groups sentences into 3–5 consecutive sentences to form QA contexts, concatenating text and preserving section context.  
      - Builds a dictionary linking each sentence (or group) to its corresponding gold questions (`CONSORT_Dict`) and answers (`Answers`).  
      - Each context contains:  
        - `PMCID` – the article identifier  
        - `Sentence_IDs` – IDs of sentences in the group  
        - `Context` – concatenated sentence text forming a QA context  
        - `CONSORT_Labels` – all labels included in the context  
        - `CONSORT_Dict` – mapping from sentence index and labels to gold questions  
        - `Answers` – mapping from sentence index and labels to sentence text  
     **Output:**  
      - `corpus_QA.xlsx` → final QA corpus with grouped contexts from all 50 PMC articles. Each row corresponds to a 3–5 sentence context with associated CONSORT labels, questions, and answers.  
      - Number of contexts corresponds to the number of 3–5 sentence groups generated across all documents.

  - **corpus_generation.py** – Script that converts the QA dataset generated by `corpus_interm.py` into a SQuAD-style JSON format suitable for training or evaluating QA models.

Functionality / Main Steps:

    1. **Load Data:**  
       - Reads `corpus_QA.xlsx` produced by `corpus_interm.py` (contains 3–5 sentence contexts, CONSORT labels, dictionaries of questions/answers).  
       - Reads `Gold.xlsx` to retrieve all Gold questions and their mapping to CONSORT items.

    2. **Prepare Dictionary Columns:**  
       - Converts the `CONSORT_Dict` and `Answers` columns from string representations to Python dictionaries using `ast.literal_eval`.

    3. **Utility Functions:**  
       - `get_answer_positions(context, answer_text)` → returns the start and end positions of an answer in the context (needed for SQuAD format).

    4. **Build SQuAD-style JSON:**  
       - Iterates over each context (3–5 sentences) and extracts all questions and answers.  
       - For each question:  
         - Skips missing questions (`"[Question not found]"`) or sentences without labels (`0`).  
         - Constructs `answers` with start and end positions in the context.  
         - Supports multiple questions per sentence.  
       - Merges consecutive QAs with the same `item_key` and same question to avoid duplicates.  
       - Handles `sub_answers` when multiple sentences correspond to the same question.

    5. **Store Information per Document:**  
       - For each document (PMCID):  
         - `doc` → article identifier  
         - `context` → full context text  
         - `context_start` and `context_end` → start/end positions of the context  
         - `qas` → list of questions with `answers` and `sub_answers`  

    6. **Save JSON:**  
       - Output file: `corpus_QA.json` → SQuAD-ready JSON.

    7. **Print Statistics:**  
       - Total number of questions.  
       - Distribution of all questions by item.  
       - Distribution ordered according to the item order in the Gold file.

  - **Outputs:**  
    - `corpus_QA.json` → SQuAD-style JSON with:  
      - `doc`: PMC ID  
      - `context`: full text of the context  
      - `qas`: questions with their answers and sub_answers  
      - `context_start`, `context_end`: positions of the context  
    - Console statistics:  
      - Total number of questions  
      - Distribution of items for all questions  
      - Distribution ordered by Gold file

#### QA Corpus Construction (SQuAD-like)

The QA corpus is built from an Excel file (`corpus_QA.xlsx`) containing, for each document:  
- **PMCID** (article identifier),  
- **Context text**,  
- A dictionary `CONSORT_Dict` mapping **questions** to CONSORT items,  
- A dictionary `Answers` containing the **corresponding answers** in the text.

Main Steps

1. **Loading and Cleaning**
   - Columns are converted to strings (`str`) and missing values are replaced with empty strings.  
   - `CONSORT_Dict` and `Answers` columns are converted into Python dictionaries using `ast.literal_eval`.

2. **Mapping Questions → Items**
   - Each key in `CONSORT_Dict` corresponds to a **CONSORT item**.  
   - Questions can be:  
     - A single question per item, or  
     - A **list of questions** for the same item.

3. **Answer Extraction**
   - For each question, the answer text is retrieved from the `Answers` dictionary.  
   - If no answer exists, a placeholder empty answer (`""`) is created with `answer_start = 0` and `answer_end = 0`.  
   - Start and end positions of answers are computed in the context to match a SQuAD-like format.

4. **Merging Consecutive QAs**
   - If **multiple consecutive questions** have the **same `item_key` and question**, their answers are **merged**.  
   - If multiple unique answers result from merging:  
     - A `sub_answers` list is created to store each answer individually.  
     - A single `answers` entry is generated by concatenating the merged answers and recalculating positions.

5. **Deduplication**
   - Duplicate answers (same text and positions) are removed.  
   - Empty answers are retained to handle cases with no information for a given item.

Corpus Characteristics
- **Multiple consecutive questions with the same item** are merged to avoid repetition.  
- **Multiple different questions can have the same answer**, but they remain separate if the question differs.  
- QAs without an answer are retained to capture missing information for an item.  
- Each QA has a **unique ID** combining the PMCID, the item, and a `_q{i}` suffix if multiple questions were merged.

Generated Statistics
- Total number of questions (i.e., questions with answers).  
- Item distribution across all questions, **ordered according to the Gold file** for comparison purposes.

### **QA_task/** 
Contains the script and outputs related to **fine-tuning and evaluating BioBERT** on the generated QA corpus.  

- **biobert.py** – Fine-tunes and evaluates the **BioBERT** model (`dmis-lab/biobert-base-cased-v1.2`) on the SQuAD-style corpus generated from CONSORT-based QA pairs.  
  - **Input:**  
    - `corpus_QA.json` → SQuAD-format file containing contexts, questions, and answers.  
  - **Main steps:**  
    - Loads the QA corpus and structures it into a DataFrame.  
    - Extracts CONSORT item numbers from `QA_ID`.  
    - Tokenizes questions and contexts with overlap handling (`stride=128`).  
    - Performs **5-fold StratifiedGroupKFold** cross-validation (grouped by PMC ID and stratified by CONSORT item).  
    - Trains the model using **multiple random seeds** for robustness.  
    - Applies post-processing to extract the best predicted answer spans (text and character positions).  
    - Prints detailed **debug outputs** showing top candidate spans and confidence scores.  
  - **Outputs:**  
    - `predictions_folds_only.xlsx` → Aggregated predictions from all folds (using the first seed).  
    - `biobert_seed{seed}_fold{fold}/` → Contains model checkpoints and logs for each fold/seed combination.

- **complete_exc.py** – Enriches the **BioBERT prediction results** with the corresponding CONSORT true labels and context information.  
  - **Input:**  
    - `predictions_folds_only.xlsx` → Output file from `biobert.py` containing all model predictions.  
    - `/QA_CONSORT/corpus_QA/corpus_QA.json` → Full corpus with all QA contexts.  
  - **Main steps:**  
    - Loads both the Excel file with predictions and the full corpus JSON.  
    - Creates a mapping between each `QA_ID` and its corresponding **context text**.  
    - Extracts **CONSORT item labels** from each `QA_ID` (e.g., `1a`, `2b`, `3a`).  
    - Adds a new column `Consort_True_Labels` to the predictions file, storing the ground truth labels.  
  - **Outputs:**  
    - `biobert_predictions_enriched.xlsx` → Final enriched Excel file containing:  
      - Original predictions  
      - Extracted CONSORT labels  
      - Mapped contexts  

- **match_type.py** – Performs a comprehensive evaluation of **BioBERT** predictions using **Exact Match**, **Partial Match**, and **Mismatch** metrics.

  - **Input:**  
    - `biobert_predictions_enriched.xlsx` → Output from `complete_exc.py`.

  - **Main steps:**  
    - Normalizes answers and computes:  
      - **Exact Match:** strict equality ignoring punctuation and case.  
      - **Partial Match:** substring overlap (prediction ⊂ answer or vice versa).  
      - **Mismatch:** no overlap (categorized further).  
    - Classifies mismatches as:  
      - `Span_vs_Empty (GT empty)`  
      - `Span_vs_Empty (Pred empty)`  
      - `Span_vs_Span`  
    - Computes **Strict** and **Lenient F1** scores per fold and per CONSORT item.  
    - Saves **visual reports** and **Excel summaries**.

  - **Outputs:**  
    - `metrics_per_fold_item.xlsx` → Contains:  
      - Sheet 1: `Detailed_Distribution`  
      - Sheet 2: `Per_Fold` (aggregated metrics by fold)  
      - Sheet 3: `Per_Item` (metrics by CONSORT item)  
      - Sheet 4: `Global_F1` (average strict/lenient scores)  
    - Several Excel exports for qualitative error analysis:  
      - `matches_exact.xlsx`, `matches_partial.xlsx`, `mismatches.xlsx`, etc.  
    - `outputs/` → Folder containing bar plots and pie charts for match categories.

- **scores_items.py** – Evaluates **BioBERT** predictions against reference answers using **ROUGE-L**, **BLEU**, and **BERTScore** metrics, while mapping each CONSORT item to its most frequent **article section** (e.g., *Methods*, *Results*, *Discussion*, etc.).

  - **Inputs:**  
    - `50_XML/` → Folder containing structured XML files for each PMC article (with section boundaries).  
    - `Gold.xlsx` → Mapping of CONSORT items and gold questions.  
    - `biobert_predictions_enriched.xlsx` → Output from `complete_exc.py`.

  - **Main steps:**  
    1. **XML parsing:** Extracts structural information from each article.  
      - Reads `<section>` tags and their `textSpan` attributes.  
      - Associates each **CONSORT item** (from XML `selection` attributes) with the correct article section.  
      - Handles equivalent section names (e.g., “Materials and Methods” → “Methods”, “Background” → “Introduction”).  
    2. **Error-tolerant matching:**  
      - If a section cannot be matched, assigns it to **“Article Beginning”**.  
      - Margin (`MARGIN = 10`) allows flexible matching for boundary offsets.  
    3. **Metrics computation:**  
      - **ROUGE-L:** F-measure of longest common subsequence.  
      - **BLEU:** N-gram precision with smoothing.  
      - **BERTScore:** Semantic similarity using contextual embeddings.  

  - **Outputs:**  
    - `outputs/biobert_predictions_with_scores_sections.xlsx` → Enriched predictions with:  
      - `CONSORT_Item`, `Section`, `Section_Equivalente`, and metric scores (`ROUGE_L`, `BLEU`, `BERTScore`).  
    - Plots (saved in `outputs/`):  
      - `ROUGE_L_per_CONSORT_Item_and_Section_grouped_compact.png`  
      - `BLEU_per_CONSORT_Item_and_Section_grouped_compact.png`  
      - `BERTScore_per_CONSORT_Item_and_Section_grouped_compact.png`  

- **section_item.py** – Associates **prediction matches** (Exact, Partial, or Mismatch) with their corresponding **article sections** and **CONSORT items** based on the XML structure of each publication.

  Despite the name, this script works for *all* match types — simply change the `MATCHES_FILE` variable to point to the desired input file (e.g., `matches_exact.xlsx`, `matches_partial.xlsx`, `mismatches.xlsx`).

  - **Inputs:**  
    - `matches_partial.xlsx` *(or any other matches file)* → Input from the evaluation phase (`match_type.py`).  
    - `/QA_CONSORT/CONSORT-TM_stats/item_distribution/50_XML/` → Folder with structured PMC XMLs.  
    - `/QA_CONSORT/AQG/mistral/Gold.xlsx` → Contains mapping between CONSORT Items and Gold Questions.  

  - **Main steps:**  
    1. **XML parsing and section mapping:**  
      - Extracts all `<section>` elements and their `textSpan` offsets.  
      - Builds a mapping between CONSORT items (from XML `selection`) and article sections.  
      - Handles equivalent section titles (e.g., “Materials and Methods” → “Methods”).  

    2. **Automatic Back Matter and “Article Beginning” handling:**  
      - Detects missing `<back>` sections automatically and adds them when needed.  
      - Assigns unmatched sentences to the **“Article Beginning”** pseudo-section (useful for incomplete XMLs).  
      - Margin (`MARGIN = 10`) allows flexible boundary matching.  

    3. **Integration with match results:**  
      - Reads the Excel file with BioBERT match outputs.  
      - Adds three new columns:  
        - `Section` → Detected section for the sentence.  
        - `Section_Equivalente` → Normalized (canonical) section name.  
        - `CONSORT_Item` → Corresponding CONSORT item number from `Gold.xlsx`.  

    4. **Error reporting:**  
      - Logs missing matches with `[NO MATCH]` in the console.  
      - Displays added Back Matter sections and Article Beginning cases.  

  - **Outputs:**  
    - `outputs/matches_with_sections_by_item_partial.xlsx` → Excel file enriched with structural information.  
      Columns include:  
      - `QA_ID`, `Question`, `CONSORT_Item`, `Section`, `Section_Equivalente`, and all original match columns.  

- **stats_match_per_item.py** – Aggregates **prediction matches** per CONSORT item and per section to provide a **quantitative overview** of item distribution across articles.

  - **Inputs:**  
    - `outputs/matches_with_sections_by_item_exact.xlsx` → Output from `matches_with_sections_by_item.py`.  
      Can also use `_partial` or `_mismatches` versions for other match types.

  - **Main steps:**  
    1. **Load the Excel file** and extract PMC prefix from `QA_ID`.  
    2. **Count occurrences**:  
       - For each `(CONSORT_Item, Section_Equivalente)` combination, count the number of appearances in each PMC.  
       - Track whether multiple sections contain the same item in the same PMC.  
    3. **Avoid duplicates** by using `QA_ID` as a unique identifier.  
    4. **Aggregate per item & section**:  
       - `Num_Documents` → Number of unique PMCs containing the item in the section.  
       - `Total_Appearances` → Total number of occurrences across all PMCs.  

  - **Outputs:**  
    - `outputs/items_section_summary_exact.xlsx` → Excel file with two sheets:  
      1. **Detailed** → Row-level counts per PMC.  
         Columns: `CONSORT_Item`, `Section_Equivalente`, `PMC`, `Count_in_Section`, `Multiple_Sections_in_Same_Document`.  
      2. **Summary** → Aggregated counts per item & section.  
         Columns: `CONSORT_Item`, `Section_Equivalente`, `Num_Documents`, `Total_Appearances`.  

- **plots_proportion.py** – Generates **proportion bar plots** of predicted matches (Exact, Partial, Mismatch) per CONSORT item and section.

  - **Inputs:**  
    - `outputs/items_section_summary_exact.xlsx` → Summary from `stats_match_per_item.py` (Exact matches).  
    - `outputs/items_section_summary_partial.xlsx` → Summary for Partial matches.  
    - `outputs/items_section_summary_mismatches.xlsx` → Summary for Mismatch predictions.  

  - **Main steps:**  
    1. Load Excel summaries for Exact, Partial, and Mismatch predictions.  
    2. Concatenate all match types and compute **proportion per item**:  
      \[
      Proportion = \frac{\text{Total appearances per section}}{\text{Total appearances across all sections for that item}}
      \]  
    3. Apply a **fixed color palette** for main sections (`Title`, `Abstract`, `Introduction`, etc.) and generate extra colors for other sections if needed.  
    4. Generate **grouped bar plots**:  
      - Each CONSORT item is a group.  
      - Bars represent proportion of matches in each section.  
      - Vertical dashed lines separate items for clarity.  
      - Values displayed on top of each bar.  
    5. Saves one plot per match type (Exact, Partial, Mismatch).  

  - **Outputs:**  
    - `outputs/items_sections_exact_proportion_grouped_sep_compact.png`  
    - `outputs/items_sections_partial_proportion_grouped_sep_compact.png`  
    - `outputs/items_sections_mismatch_proportion_grouped_sep_compact.png`  

- **Plots_metricsQA_folds.ipynb** – Computes and plots **BERTScore, ROUGE-L, and BLEU** metrics per fold for different match types (Exact, Partial, Mismatches, and overall BioBERT predictions).

  - **Inputs:**  
    - `matches_exact.xlsx` → Exact Match predictions.  
    - `matches_partial.xlsx` → Partial Match predictions.  
    - `mismatches.xlsx` → Mismatch predictions.  
    - `biobert_predictions_enriched.xlsx` → All predictions for global metrics.

  - **Main steps:**  
    1. Load prediction files and extract reference answers and predicted answers.  
    2. Compute metrics:  
      - **BERTScore F1**  
      - **ROUGE-L F1**  
      - **BLEU** (nltk, no smoothing)  
    3. Aggregate metrics **per fold** and compute **average across folds**.  
    4. Generate **bar plots per metric per fold** with a red dashed line showing the global average.  
    5. Save both **Excel summary files** and **plots** per match type.

  - **Outputs:**  
    - Excel summary per fold, e.g.:  
      - `results_metrics_fold_match_exact.xlsx`  
      - `results_metrics_fold_match_partial.xlsx`  
      - `results_metrics_fold_mismatches.xlsx`  
      - `results_metrics_fold.xlsx` (global)  
    - Bar plots per metric and fold saved in corresponding folders:  
      - `plots_fold_match_exact/`  
      - `plots_fold_match_partial/`  
      - `plots_fold_mismatches/`  
      - `plots_fold_seed/` (global)  

- **environment.yml** – Conda environment file with all dependencies  
- **README.md** – Project documentation (this file)

