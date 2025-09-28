import os
import io
import base64
import numpy as np
from PIL import Image
import pydicom
import torch
from transformers import CLIPProcessor, CLIPModel
from sqlalchemy import create_engine, text

# ----------------------------
# PostgreSQL connection
# ----------------------------
engine = create_engine("postgresql://postgres:postgres@localhost:5432/bikedb")

# ----------------------------
# Load Hugging Face CLIP
# ----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# ----------------------------
# Data folder
# ----------------------------
root_dir = "./data/test_MRI_Data"

# ----------------------------
# Metadata extraction
# ----------------------------
def extract_metadata(file_path):
    ds = pydicom.dcmread(file_path, stop_before_pixels=True)
    return {
        "study_instance_uid": getattr(ds, "StudyInstanceUID", None),
        "series_instance_uid": getattr(ds, "SeriesInstanceUID", None),
        "sop_instance_uid": getattr(ds, "SOPInstanceUID", None),
        "modality": getattr(ds, "Modality", None),
        "study_description": getattr(ds, "StudyDescription", None),
        "procedure_description": getattr(ds, "RequestedProcedureDescription", None),
        "series_number": getattr(ds, "SeriesNumber", None),
        "series_description": getattr(ds, "SeriesDescription", None),
        "manufacturer": getattr(ds, "Manufacturer", None),
        "model_name": getattr(ds, "ManufacturerModelName", None),
        "magnetic_field_strength": getattr(ds, "MagneticFieldStrength", None),
        "instance_number": getattr(ds, "InstanceNumber", None),
        "slice_thickness": getattr(ds, "SliceThickness", None),
        "pixel_spacing": str(getattr(ds, "PixelSpacing", None)),
        "image_position": str(getattr(ds, "ImagePositionPatient", None)),
        "image_orientation": str(getattr(ds, "ImageOrientationPatient", None)),
        "file_path": file_path,
    }

# ----------------------------
# Encode base64
# ----------------------------
def encode_base64(file_path):
    ds = pydicom.dcmread(file_path)
    arr = ds.pixel_array.astype(np.float32)
    slope = getattr(ds, "RescaleSlope", 1)
    intercept = getattr(ds, "RescaleIntercept", 0)
    arr = arr * slope + intercept

    wc = getattr(ds, "WindowCenter", None)
    ww = getattr(ds, "WindowWidth", None)
    if wc is not None and ww is not None:
        if isinstance(wc, pydicom.multival.MultiValue):
            wc = float(wc[0])
        if isinstance(ww, pydicom.multival.MultiValue):
            ww = float(ww[0])
        arr = np.clip(arr, wc - ww/2, wc + ww/2)
    else:
        arr = np.clip(arr, arr.min(), arr.max())

    arr = ((arr - arr.min()) / (arr.max() - arr.min()) * 255.0).astype(np.uint8)
    img = Image.fromarray(arr)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

# ----------------------------
# Base64 -> embedding (Hugging Face CLIP)
# ----------------------------
def get_embedding_from_base64(b64_string):
    img = Image.open(io.BytesIO(base64.b64decode(b64_string))).convert("RGB")
    inputs = processor(images=img, return_tensors="pt").to(device)
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding[0].cpu().numpy().tolist()  # 512-d vector

# ----------------------------
# Main loop
# ----------------------------
with engine.connect() as conn:
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

            try:
                # Patients table
                conn.execute(
                    text("INSERT INTO patients (patient_id) VALUES (:pid) ON CONFLICT DO NOTHING"),
                    {"pid": patient_id},
                )
                conn.commit()

                meta = extract_metadata(file_path)

                # Studies table
                conn.execute(
                    text("""
                        INSERT INTO studies (study_instance_uid, patient_id, modality, study_description, procedure_description)
                        VALUES (:study_instance_uid, :pid, :modality, :study_description, :procedure_description)
                        ON CONFLICT (study_instance_uid) DO NOTHING
                    """),
                    {"pid": patient_id, **meta}
                )
                conn.commit()

                # Series table
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
                conn.commit()

                # Instances table
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
                conn.commit()

                # Base64 + embedding
                b64_data = encode_base64(file_path)
                embedding_vector = get_embedding_from_base64(b64_data)
            
                # Insert into instance_images
                conn.execute(
                    text("""
                        INSERT INTO instance_images (sop_instance_uid, file_path, base64_data, embedding)
                        VALUES (:sop_instance_uid, :file_path, :b64, :emb)
                        ON CONFLICT (sop_instance_uid) DO NOTHING
                    """),
                    {
                        "sop_instance_uid": meta["sop_instance_uid"],
                        "file_path": file_path,
                        "b64": b64_data,
                        "emb": embedding_vector
                    }
                )
                conn.commit()
                print(f"✅ Inserted {fname} for patient {patient_id} with embedding")

            except Exception as e:
                conn.rollback()
                print(f"⚠️ Failed {file_path}: {e}")