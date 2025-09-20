-- Drop tables if they exist (for testing/reload)
DROP TABLE IF EXISTS dicom_metadata CASCADE;
DROP TABLE IF EXISTS extra_findings CASCADE;
DROP TABLE IF EXISTS findings CASCADE;
DROP TABLE IF EXISTS spine_levels CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY
);

-- reports table (text reports from Excel)
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

-- dicom_metadata table (MRI/CT image metadata)
CREATE TABLE IF NOT EXISTS dicom_metadata (
    dicom_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),

    -- Identifiers
    study_instance_uid TEXT,
    series_instance_uid TEXT,
    sop_instance_uid TEXT UNIQUE,

    -- Patient info
    sex VARCHAR(10),
    age VARCHAR(10),
    height FLOAT,
    weight FLOAT,

    -- Study info
    modality VARCHAR(20),
    study_description TEXT,
    procedure_description TEXT,

    -- Series info
    series_number INT,
    series_description TEXT,

    -- Image info
    instance_number INT,
    slice_thickness FLOAT,
    pixel_spacing TEXT,
    image_position TEXT,
    image_orientation TEXT,

    -- Scanner info
    manufacturer TEXT,
    model_name TEXT,
    magnetic_field_strength FLOAT,

    -- File location
    file_path TEXT
);

-- Indexes for faster queries
CREATE INDEX idx_reports_tsv ON reports USING GIN(report_tsv);
CREATE INDEX idx_spine_levels_region ON spine_levels(region);
CREATE INDEX idx_findings_type ON findings(finding_type);
CREATE INDEX idx_dicom_patient ON dicom_metadata(patient_id);
CREATE INDEX idx_dicom_series ON dicom_metadata(series_instance_uid);
CREATE INDEX idx_dicom_modality ON dicom_metadata(modality);