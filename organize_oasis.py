import os
import shutil

# === SETTINGS ===
source_root = r"C:\Users\aregk\Downloads\oasis_cross-sectional_disc12\disc12"
output_root = r"C:\Users\aregk\OneDrive\Desktop\Thesis_downoading_the_data"

# === MAIN ===
for patient_folder in os.listdir(source_root):
    # Only process MR1 folders (e.g. OAS1_0029_MR1)
    if not patient_folder.endswith("_MR1"):
        continue

    processed_path = os.path.join(source_root, patient_folder, "PROCESSED")
    if not os.path.isdir(processed_path):
        continue

    # Extract patient ID (e.g. OAS1_0029)
    patient_id = "_".join(patient_folder.split("_")[:2])

    # Create output folder for this patient
    patient_output = os.path.join(output_root, patient_id)
    os.makedirs(patient_output, exist_ok=True)

    # Walk through all subdirectories in PROCESSED
    for dirpath, _, files in os.walk(processed_path):
        for file in files:
            if file.lower().endswith(".gif"):
                src = os.path.join(dirpath, file)
                dst = os.path.join(patient_output, file)
                shutil.copy2(src, dst)
                print(f"Copied: {file} → {patient_id}/")

print("\nDone!")