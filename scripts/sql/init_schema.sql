-- Drop tables if they exist (for testing)
DROP TABLE IF EXISTS extra_findings CASCADE;
DROP TABLE IF EXISTS findings CASCADE;
DROP TABLE IF EXISTS spine_levels CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY
);

-- reports table
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    raw_text TEXT,
    cleaned_text TEXT,
    word_count INT,
    report_tsv tsvector
);

-- spine_levels table
CREATE TABLE IF NOT EXISTS spine_levels (
    level_id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(report_id),
    region VARCHAR(10),
    vertebra_start VARCHAR(10),
    vertebra_end VARCHAR(10)
);

-- findings table
CREATE TABLE IF NOT EXISTS findings (
    finding_id SERIAL PRIMARY KEY,
    level_id INT REFERENCES spine_levels(level_id),
    finding_type VARCHAR(50),
    severity VARCHAR(20),
    laterality VARCHAR(20)
);

-- extra findings table (incidental notes not tied to levels)
CREATE TABLE IF NOT EXISTS extra_findings (
    extra_id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(report_id),
    description TEXT
);


-- Indexes for faster query
CREATE INDEX idx_reports_tsv ON reports USING GIN(report_tsv);
CREATE INDEX idx_spine_levels_region ON spine_levels(region);
CREATE INDEX idx_findings_type ON findings(finding_type);
