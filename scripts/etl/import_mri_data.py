import os
import pydicom
from sqlalchemy import create_engine, text

# DB connection
engine = create_engine("postgresql://postgres:postgres@localhost:5432/bikedb")

# Root folder of your DICOM dataset
root_dir = "./data/test_MRI_Data"

def extract_metadata(file_path):
    """Read a DICOM file and return a dict of useful metadata"""
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        return {
            # Identifiers
            "study_instance_uid": getattr(ds, "StudyInstanceUID", None),
            "series_instance_uid": getattr(ds, "SeriesInstanceUID", None),
            "sop_instance_uid": getattr(ds, "SOPInstanceUID", None),

            # Patient info
            "sex": getattr(ds, "PatientSex", None),
            "age": getattr(ds, "PatientAge", None),
            "height": getattr(ds, "PatientSize", None),
            "weight": getattr(ds, "PatientWeight", None),

            # Study info
            "modality": getattr(ds, "Modality", None),
            "study_description": getattr(ds, "StudyDescription", None),
            "procedure_description": getattr(ds, "RequestedProcedureDescription", None),

            # Series info
            "series_number": getattr(ds, "SeriesNumber", None),
            "series_description": getattr(ds, "SeriesDescription", None),

            # Image info
            "instance_number": getattr(ds, "InstanceNumber", None),
            "slice_thickness": getattr(ds, "SliceThickness", None),
            "pixel_spacing": str(getattr(ds, "PixelSpacing", None)),
            "image_position": str(getattr(ds, "ImagePositionPatient", None)),
            "image_orientation": str(getattr(ds, "ImageOrientationPatient", None)),

            # Scanner info
            "manufacturer": getattr(ds, "Manufacturer", None),
            "model_name": getattr(ds, "ManufacturerModelName", None),
            "magnetic_field_strength": getattr(ds, "MagneticFieldStrength", None),

            # File path
            "file_path": file_path,
        }
    except Exception as e:
        print(f"⚠️ Failed to parse {file_path}: {e}")
        return None


with engine.begin() as conn:
    for root, _, files in os.walk(root_dir):
        for fname in files:
            if fname.lower().endswith(".ima"):
                file_path = os.path.join(root, fname)

                # Extract patient_id from first-level folder (0001, 0002, …)
                relative_path = os.path.relpath(root, root_dir)
                patient_folder = relative_path.split(os.sep)[0]
                patient_id = int(patient_folder) if patient_folder.isdigit() else None

                if patient_id:
                    conn.execute(
                        text("INSERT INTO patients (patient_id) VALUES (:pid) ON CONFLICT DO NOTHING"),
                        {"pid": patient_id},
                    )

                meta = extract_metadata(file_path)
                if meta:
                    conn.execute(
                        text("""
                            INSERT INTO dicom_metadata (
                                patient_id, study_instance_uid, series_instance_uid,
                                sop_instance_uid, sex, age, height, weight,
                                modality, study_description, procedure_description,
                                series_number, series_description,
                                instance_number, slice_thickness, pixel_spacing,
                                image_position, image_orientation,
                                manufacturer, model_name, magnetic_field_strength,
                                file_path
                            )
                            VALUES (
                                :patient_id, :study_instance_uid, :series_instance_uid,
                                :sop_instance_uid, :sex, :age, :height, :weight,
                                :modality, :study_description, :procedure_description,
                                :series_number, :series_description,
                                :instance_number, :slice_thickness, :pixel_spacing,
                                :image_position, :image_orientation,
                                :manufacturer, :model_name, :magnetic_field_strength,
                                :file_path
                            )
                            ON CONFLICT (sop_instance_uid) DO NOTHING
                        """),
                        {"patient_id": patient_id, **meta}
                    )
                    print(f"✅ Inserted {fname} for patient {patient_id}")
