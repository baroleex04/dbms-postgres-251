import pandas as pd
import re
import nltk
from sqlalchemy import create_engine, text

# Download necessary tokenizers
nltk.download("punkt")
nltk.download("punkt_tab")

# Connect to Postgres
engine = create_engine("postgresql://postgres:postgres@localhost:5432/bikedb")

# Load Excel
file_path = "./data/Radiologists Report.xlsx"
df = pd.read_excel(file_path)

# --- Normalize column names ---
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Fix weird apostrophe column names if present
rename_map = {}
for col in df.columns:
    if "clinician" in col:  # catch clinician's_notes or similar
        rename_map[col] = "clinicians_notes"
df.rename(columns=rename_map, inplace=True)

def clean_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_spine_levels(text):
    text = text.upper()
    pattern = r'([CLDS]\d{1,2})(?:[-/](?:([CLDS])?(\d{1,2})))?'
    matches = re.findall(pattern, text)
    levels = []
    for start_full, region2, num2 in matches:
        region1 = start_full[0]
        start = start_full
        if num2:
            end_region = region2 if region2 else region1
            end = f"{end_region}{num2}"
        else:
            end = start
        levels.append((region1, start, end))
    return levels

def extract_findings(text):
    findings = []
    t = text.lower()
    patterns = {
        "bulge": [r"disc\s+bulge", r"bulges", r"broad[- ]based\s+bulge"],
        "protrusion": [r"protrusion", r"extrusion", r"sequestrated", r"sequestered"],
        "herniation": [r"herniation", r"disc\s+hernia"],
        "annular_tear": [r"annular\s+tear"],
        "stenosis": [r"stenosis", r"canal\s+stenosis", r"foraminal\s+stenosis"],
        "fracture": [r"fracture", r"compression\s+fracture"],
        "spondylolisthesis": [r"spondylolisthesis", r"listhesis"],
        "degeneration": [r"degeneration", r"modic", r"endplate\s+changes"],
        "schmorl": [r"schmorl"],
        "cyst": [r"cyst", r"tarlov\s+cyst", r"renal\s+cyst", r"pelvic\s+cyst"],
        "lipoma": [r"lipoma"],
        "hemangioma": [r"hemangioma"]
    }
    severity_map = {"mild": "mild", "moderate": "moderate", "severe": "severe"}
    laterality_map = {"left": "left", "right": "right", "bilateral": "bilateral"}

    for ftype, regex_list in patterns.items():
        for rgx in regex_list:
            if re.search(rgx, t):
                sev = next((s for s in severity_map if s in t), None)
                lat = next((l for l in laterality_map if l in t), None)
                findings.append((ftype, sev, lat))
                break
    return findings


# --- Insert into DB ---
with engine.begin() as conn:
    print(f"📌 Connected to DB: {engine.url.database}, server: {engine.url.host}")

    for _, row in df.iterrows():
        pid = int(row.get("patient_id"))
        raw = str(row.get("clinicians_notes") or "").replace("\x00", "")
        clean = clean_text(raw)
        tokens = nltk.word_tokenize(clean)
        wc = len(tokens)

        print(f"➡️ Inserting patient {pid}, raw length={len(raw)}, preview={raw[:60]}")

        # Step 1: ensure patient exists
        conn.execute(
            text("""
                INSERT INTO patients (patient_id)
                VALUES (:pid)
                ON CONFLICT (patient_id) DO NOTHING
            """),
            {"pid": pid},
        )

        # Step 2: insert report
        result = conn.execute(
            text("""
                INSERT INTO reports (patient_id, raw_text, cleaned_text, word_count, report_tsv)
                VALUES (:pid, :raw, :clean, :wc, to_tsvector(:clean))
                RETURNING report_id
            """),
            {"pid": pid, "raw": raw, "clean": clean, "wc": wc},
        )
        report_id = result.scalar()

        # Step 3: insert spine levels
        levels = extract_spine_levels(raw)
        for region, start, end in levels:
            res = conn.execute(
                text("""
                    INSERT INTO spine_levels (report_id, region, vertebra_start, vertebra_end)
                    VALUES (:rid, :region, :vs, :ve)
                    RETURNING level_id
                """),
                {"rid": report_id, "region": region, "vs": start, "ve": end},
            )
            level_id = res.scalar()

            # Step 4: insert findings for each level
            for ftype, sev, lat in extract_findings(raw):
                conn.execute(
                    text("""
                        INSERT INTO findings (level_id, finding_type, severity, laterality)
                        VALUES (:lid, :ftype, :sev, :lat)
                    """),
                    {"lid": level_id, "ftype": ftype, "sev": sev, "lat": lat},
                )

        # Step 5: insert extra findings (not tied to spine level)
        if any(word in clean for word in ["cyst", "lipoma", "hemangioma"]):
            conn.execute(
                text("""
                    INSERT INTO extra_findings (report_id, description)
                    VALUES (:rid, :desc)
                """),
                {"rid": report_id, "desc": raw},
            )

print("✅ Data imported into structured schema")
