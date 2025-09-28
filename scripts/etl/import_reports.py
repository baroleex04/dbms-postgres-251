import pandas as pd
import re
import nltk
from sqlalchemy import create_engine, text
import nltk
nltk.download("punkt_tab")

# nltk.download("punkt")

engine = create_engine("postgresql://postgres:postgres@localhost:5432/bikedb")
file_path = "./data/Radiologists Report.xlsx"
df = pd.read_excel(file_path)

# Normalize column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
rename_map = {c: "clinicians_notes" for c in df.columns if "clinician" in c}
df.rename(columns=rename_map, inplace=True)


# -------------------------------
# Utility functions
# -------------------------------
def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_spine_levels(text: str):
    text = text.upper()
    pattern = r"([CLDS]\d{1,2})(?:[-/](?:([CLDS])?(\d{1,2})))?"
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


def extract_findings(text: str):
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
        "hemangioma": [r"hemangioma"],
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


# -------------------------------
# MRI Section Splitting
# -------------------------------
MRI_HEADERS = [
    r"(LSS MRI)",
    r"(Lumbosacral MRI)",
    r"(Cervical spine MRI|Cervical MRI)",
    r"(Thoracic MRI)",
    r"(Lumbar MRI)",
]

split_pattern = re.compile("|".join(MRI_HEADERS), re.IGNORECASE)


def split_mri_sections(raw_text: str):
    """
    Splits raw text into (study_type, description) tuples.
    Uses header end to ensure multiple MRI sections (like case 272) are captured.
    """
    if not raw_text:
        return []

    matches = list(split_pattern.finditer(raw_text))
    if not matches:
        return [("MRI", raw_text.strip())]

    sections = []
    for i, m in enumerate(matches):
        header = m.group(0).strip()
        start = m.end()  # <--- FIX: start after header
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        body = raw_text[start:end].strip(" :\n")
        sections.append((header, body))
    return sections


# -------------------------------
# ETL Main
# -------------------------------
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

        # Step 2: insert ONE report row (original Excel text)
        result = conn.execute(
            text("""
                INSERT INTO reports (patient_id, raw_text, cleaned_text, word_count, report_tsv)
                VALUES (:pid, :raw, :clean, :wc, to_tsvector(:clean))
                RETURNING report_id
            """),
            {"pid": pid, "raw": raw, "clean": clean, "wc": wc},
        )
        report_id = result.scalar()

        # Step 3: insert spine levels from full raw text
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

            for ftype, sev, lat in extract_findings(raw):
                conn.execute(
                    text("""
                        INSERT INTO findings (level_id, finding_type, severity, laterality)
                        VALUES (:lid, :ftype, :sev, :lat)
                    """),
                    {"lid": level_id, "ftype": ftype, "sev": sev, "lat": lat},
                )

        # Step 4: insert extra findings (split sections)
        sections = split_mri_sections(raw)
        for study_type, desc in sections:
            conn.execute(
                text("""
                    INSERT INTO extra_findings (report_id, study_type, description)
                    VALUES (:rid, :stype, :desc)
                """),
                {"rid": report_id, "stype": study_type, "desc": desc},
            )

print("✅ Data imported into structured schema")