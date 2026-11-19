import os
import re
import shutil
import pandas as pd

# --- Adjust these to match your setup ---
images_dir = r"C:\Users\odoya\OneDrive\Documents\Passion_dataset\PASSION_MICCAI_2024\images"           # folder containing the jpg files
labels_csv = r"C:\Users\odoya\OneDrive\Documents\Passion_dataset\PASSION_MICCAI_2024\label.csv"        # csv file with labels
output_dir = r"C:\Users\odoya\OneDrive\Documents\Passion_dataset\PASSION_MICCAI_2024\paediatric_images" # new folder to create
id_col = "subject_id"        
age_col = "age"                  

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(labels_csv)
df.columns = df.columns.str.strip()
df[id_col] = df[id_col].astype(str).str.strip()
df[age_col] = pd.to_numeric(df[age_col], errors="coerce")

# Lookup: subject_id -> age (one row per subject)
age_lookup = df.drop_duplicates(subset=id_col).set_index(id_col)[age_col].to_dict()

copied, no_label = 0, []
for fname in os.listdir(images_dir):
    if not fname.lower().endswith((".jpg", ".jpeg")):
        continue
    stem = os.path.splitext(fname)[0]
    subject_id = re.sub(r"_\d+$", "", stem)   # AA00970008_1 -> AA00970008

    age = age_lookup.get(subject_id)
    if age is None:
        no_label.append(fname)
    elif age < 18:
        shutil.copy2(os.path.join(images_dir, fname), os.path.join(output_dir, fname))
        copied += 1

# Save matching labels for the paediatric subset
paeds = df[df[age_col] < 18]
paeds.to_csv(os.path.join(output_dir, "paediatric_labels.csv"), index=False)

print(f"Copied {copied} images to '{output_dir}'")
if no_label:
    print(f"{len(no_label)} images had no matching subject_id in the CSV, e.g. {no_label[:5]}")