-- Drop tables if they exist (for testing/reload)
-- DROP TABLE IF EXISTS dicom_metadata CASCADE;
DROP TABLE IF EXISTS extra_findings CASCADE;
DROP TABLE IF EXISTS findings CASCADE;
DROP TABLE IF EXISTS spine_levels CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS patients CASCADE;

-- patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT PRIMARY KEY
);

-- reports table (raw Excel content only)
CREATE TABLE IF NOT EXISTS reports (
    report_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    raw_text TEXT,             -- whole Excel clinician notes
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

-- extra findings table (study-type specific subsections)
CREATE TABLE IF NOT EXISTS extra_findings (
    extra_id SERIAL PRIMARY KEY,
    report_id INT REFERENCES reports(report_id),
    study_type VARCHAR(100),   -- LSS MRI, Cervical MRI, etc.
    description TEXT           -- text of that subsection
);

-- dicom_metadata table (MRI/CT image metadata)
-- CREATE TABLE IF NOT EXISTS dicom_metadata (
--     dicom_id SERIAL PRIMARY KEY,
--     patient_id INT REFERENCES patients(patient_id),
--     study_instance_uid TEXT,
--     series_instance_uid TEXT,
--     sop_instance_uid TEXT UNIQUE,
--     sex VARCHAR(10),
--     age VARCHAR(10),
--     height FLOAT,
--     weight FLOAT,
--     modality VARCHAR(20),
--     study_description TEXT,
--     procedure_description TEXT,
--     series_number INT,
--     series_description TEXT,
--     instance_number INT,
--     slice_thickness FLOAT,
--     pixel_spacing TEXT,
--     image_position TEXT,
--     image_orientation TEXT,
--     manufacturer TEXT,
--     model_name TEXT,
--     magnetic_field_strength FLOAT,
--     file_path TEXT
-- );

-- Drop old single-table version
DROP TABLE IF EXISTS instances CASCADE;
DROP TABLE IF EXISTS series CASCADE;
DROP TABLE IF EXISTS studies CASCADE;

-- Studies table (one per StudyInstanceUID)
CREATE TABLE IF NOT EXISTS studies (
    study_instance_uid TEXT PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    modality VARCHAR(20),
    study_description TEXT,
    procedure_description TEXT
);

-- Series table (one per SeriesInstanceUID)
CREATE TABLE IF NOT EXISTS series (
    series_instance_uid TEXT PRIMARY KEY,
    study_instance_uid TEXT REFERENCES studies(study_instance_uid),
    series_number INT,
    series_description TEXT,
    manufacturer TEXT,
    model_name TEXT,
    magnetic_field_strength FLOAT
);

-- Instances table (one per SOPInstanceUID = one image)
CREATE TABLE IF NOT EXISTS instances (
    sop_instance_uid TEXT PRIMARY KEY,
    series_instance_uid TEXT REFERENCES series(series_instance_uid),
    instance_number INT,
    slice_thickness FLOAT,
    pixel_spacing TEXT,
    image_position TEXT,
    image_orientation TEXT,
    file_path TEXT
);

-- Indexes for query speed
CREATE INDEX idx_studies_patient ON studies(patient_id);
CREATE INDEX idx_series_study ON series(study_instance_uid);
CREATE INDEX idx_instances_series ON instances(series_instance_uid);

-- Indexes
CREATE INDEX idx_reports_tsv ON reports USING GIN(report_tsv);
CREATE INDEX idx_spine_levels_region ON spine_levels(region);
CREATE INDEX idx_findings_type ON findings(finding_type);
CREATE INDEX idx_extra_study_type ON extra_findings(study_type);
-- CREATE INDEX idx_dicom_patient ON dicom_metadata(patient_id);
-- CREATE INDEX idx_dicom_series ON dicom_metadata(series_instance_uid);
-- CREATE INDEX idx_dicom_modality ON dicom_metadata(modality);