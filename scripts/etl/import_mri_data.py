import os
import pydicom
from sqlalchemy import create_engine, text

# DB connection
engine = create_engine("postgresql://postgres:postgres@localhost:5432/bikedb")

root_dir = "./data/test_MRI_Data"

def extract_metadata(file_path):
    """Extract normalized DICOM metadata"""
    ds = pydicom.dcmread(file_path, stop_before_pixels=True)
    return {
        "study_instance_uid": getattr(ds, "StudyInstanceUID", None),
        "series_instance_uid": getattr(ds, "SeriesInstanceUID", None),
        "sop_instance_uid": getattr(ds, "SOPInstanceUID", None),

        # Study
        "modality": getattr(ds, "Modality", None),
        "study_description": getattr(ds, "StudyDescription", None),
        "procedure_description": getattr(ds, "RequestedProcedureDescription", None),

        # Series
        "series_number": getattr(ds, "SeriesNumber", None),
        "series_description": getattr(ds, "SeriesDescription", None),
        "manufacturer": getattr(ds, "Manufacturer", None),
        "model_name": getattr(ds, "ManufacturerModelName", None),
        "magnetic_field_strength": getattr(ds, "MagneticFieldStrength", None),

        # Instance
        "instance_number": getattr(ds, "InstanceNumber", None),
        "slice_thickness": getattr(ds, "SliceThickness", None),
        "pixel_spacing": str(getattr(ds, "PixelSpacing", None)),
        "image_position": str(getattr(ds, "ImagePositionPatient", None)),
        "image_orientation": str(getattr(ds, "ImageOrientationPatient", None)),

        "file_path": file_path,
    }

with engine.begin() as conn:
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if not fname.lower().endswith(".ima"):
                continue

            file_path = os.path.join(root, fname)
            relative_path = os.path.relpath(root, root_dir)
            patient_folder = relative_path.split(os.sep)[0]
            patient_id = int(patient_folder) if patient_folder.isdigit() else None
            if not patient_id:
                continue

            # Ensure patient exists
            conn.execute(
                text("INSERT INTO patients (patient_id) VALUES (:pid) ON CONFLICT DO NOTHING"),
                {"pid": patient_id},
            )

            try:
                meta = extract_metadata(file_path)
            except Exception as e:
                print(f"⚠️ Failed to parse {file_path}: {e}")
                continue

            # Insert study
            conn.execute(
                text("""
                    INSERT INTO studies (study_instance_uid, patient_id, modality, study_description, procedure_description)
                    VALUES (:study_instance_uid, :pid, :modality, :study_description, :procedure_description)
                    ON CONFLICT (study_instance_uid) DO NOTHING
                """),
                {"pid": patient_id, **meta}
            )

            # Insert series
            conn.execute(
                text("""
                    INSERT INTO series (series_instance_uid, study_instance_uid, series_number, series_description,
                                        manufacturer, model_name, magnetic_field_strength)
                    VALUES (:series_instance_uid, :study_instance_uid, :series_number, :series_description,
                            :manufacturer, :model_name, :magnetic_field_strength)
                    ON CONFLICT (series_instance_uid) DO NOTHING
                """),
                meta
            )

            # Insert instance
            conn.execute(
                text("""
                    INSERT INTO instances (sop_instance_uid, series_instance_uid, instance_number, slice_thickness,
                                           pixel_spacing, image_position, image_orientation, file_path)
                    VALUES (:sop_instance_uid, :series_instance_uid, :instance_number, :slice_thickness,
                            :pixel_spacing, :image_position, :image_orientation, :file_path)
                    ON CONFLICT (sop_instance_uid) DO NOTHING
                """),
                meta
            )

            print(f"✅ Inserted {fname} for patient {patient_id}")
