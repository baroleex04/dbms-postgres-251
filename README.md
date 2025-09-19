# dbms-postgres-251

## Run command
```
docker compose up -d
```

## Access the container and use database `bikedb`
```
 docker exec -it pg_container psql -U postgres -d bikedb
```

### Import data into PostgreSQL container
In CLI: Run queries in file `0.create_table.sql` (located in `scripts/sql/`)

### Query data and functionality testing
- Go to your browser, paste the URL `localhost:8082` to access the `pgadmin` - a UI for easy monitoring and testing Postgre database system properties.
- Testing queries are located in folder `scripts/sql`, with each file represents a functionality in Postgre DBS.

## Shutdown command
```
docker compose down -v
<!-- sudo rm -rf data -->
```

## Next step
- Process text data as usable (from 1 to multi columns)
```
make up
make init-db
make etl
```
login to pgadmin as account in docker compose and check

- Import metadata into postgres

- Generate fake data for text data (for performance measurement of DBMS) - no impact on root dataset

- Identify necessary column (measure criticality) - useless ones

- Output as script (reusable)

- Identify business requirements - prompt as stakeholders

- Centralize image (if possible)

# 📊 Schema Explanation

Your ETL pipeline takes **Excel data** (`Patient ID`, `Clinician’s Notes`) and organizes it into multiple related tables. Here’s the meaning of each:

---

### 1. **patients**

```sql
CREATE TABLE patients (
    patient_id INT PRIMARY KEY
);
```

* Stores a **unique patient ID**.
* This ensures that every report can be linked to the correct patient.
* Prevents duplicate IDs with a `PRIMARY KEY`.

**Example row:**

| patient\_id |
| ----------- |
| 541         |

---

### 2. **reports**

```sql
CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    raw_text TEXT,
    cleaned_text TEXT,
    word_count INT,
    report_tsv tsvector
);
```

* Each Excel row becomes a **report record**.
* Fields:

  * `raw_text`: original clinical note (from Excel).
  * `cleaned_text`: lowercased, punctuation-stripped version.
  * `word_count`: number of tokens (useful for QA and analytics).
  * `report_tsv`: a `tsvector` column → supports **Postgres full-text search**.

**Example row:**

| report\_id | patient\_id | raw\_text                  | cleaned\_text          | word\_count | report\_tsv        |
| ---------- | ----------- | -------------------------- | ---------------------- | ----------- | ------------------ |
| 1          | 541         | “L4-5: Mild disc bulge...” | “l4 5 mild disc bulge” | 12          | `'bulge':3 'disc'` |

---

### 3. **spine\_levels**

```sql
CREATE TABLE spine_levels (
    level_id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(report_id),
    region VARCHAR(10),
    vertebra_start VARCHAR(10),
    vertebra_end VARCHAR(10)
);
```

* Extracts **spinal levels** mentioned in the notes (e.g., `L4-L5`, `C5-C6`).
* Normalizes text like `L5/S1` into structured start/end vertebrae.
* Linked to the specific report (`report_id`).

**Example row:**

| level\_id | report\_id | region | vertebra\_start | vertebra\_end |
| --------- | ---------- | ------ | --------------- | ------------- |
| 10        | 1          | L      | L4              | L5            |

---

### 4. **findings**

```sql
CREATE TABLE findings (
    finding_id SERIAL PRIMARY KEY,
    level_id INT REFERENCES spine_levels(level_id),
    finding_type VARCHAR(50),
    severity VARCHAR(20),
    laterality VARCHAR(20)
);
```

* Extracts **structured findings** per spine level:

  * `finding_type`: bulge, protrusion, herniation, stenosis, fracture, etc.
  * `severity`: mild, moderate, severe.
  * `laterality`: left, right, bilateral.
* Each finding is tied to a specific **spine level**.

**Example row:**

| finding\_id | level\_id | finding\_type | severity | laterality |
| ----------- | --------- | ------------- | -------- | ---------- |
| 101         | 10        | bulge         | mild     | left       |

---

### 5. **extra\_findings**

```sql
CREATE TABLE extra_findings (
    extra_id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(report_id),
    description TEXT
);
```

* Stores findings **not tied to a specific vertebral level**, but still important.
* Example: cysts, lipomas, hemangiomas.
* Linked directly to the `report_id`.

**Example row:**

| extra\_id | report\_id | description                      |
| --------- | ---------- | -------------------------------- |
| 12        | 1          | “Incidental finding: renal cyst” |

---

### 6. **Indexes**

```sql
CREATE INDEX idx_reports_tsv ON reports USING GIN(report_tsv);
CREATE INDEX idx_spine_levels_region ON spine_levels(region);
CREATE INDEX idx_findings_type ON findings(finding_type);
```

* **`idx_reports_tsv`**: makes full-text searches (`@@ to_tsquery`) fast.
* **`idx_spine_levels_region`**: speeds up queries by spine region (e.g., all lumbar cases).
* **`idx_findings_type`**: makes counting/filtering by finding type (e.g., bulge vs stenosis) efficient.

---

# 🚀 Why This Schema is Useful

By splitting Excel notes into these **normalized tables**:

* ✅ Patients → unique identifiers.
* ✅ Reports → keep original + cleaned notes for NLP and audit.
* ✅ Spine levels → structured vertebral references.
* ✅ Findings → structured pathologies with severity + laterality.
* ✅ Extra findings → capture incidental info.
* ✅ Indexes → optimize performance for text mining and analytics.
