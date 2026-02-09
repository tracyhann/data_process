import os

root = os.path.join("/media/ttt", "Extreme SSD", "ADNI_1111/ADNIdcm")
lines = []
for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
    for name in filenames:
        full = os.path.join(dirpath, name)
        # do something with each file
        lines.append(full)
lines

# ADNI_068_S_0210_
pts = []
for line in lines:
    dir = line.split('/')[-1]
    pt = dir.split('_')[:4]
    pt = '_'.join(pt)
    pts.append(pt)

pts = list(set(pts))   
len(pts)

with open("/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/input.txt", "w", encoding="utf-8") as f:
    for line in lines[:]:
        if 'GradWarp/' in line:
            line = line.replace('/media/ttt/Extreme SSD/ADNI_1111/ADNIdcm', '/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/raw')
            f.write(f"{line}\n")  # ensures newline



with open("/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/output.txt", "w", encoding="utf-8") as f:
    for line in lines[:]:
        if 'GradWarp/' in line:
            dir = line.split('/')[-1]
            dir = dir.replace('.nii', '')
            f.write(f"/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/turboprep_out/{dir}\n")  # ensures newline

len(lines)


import os
import shutil

list_file = "/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/input.txt"   # path to your text file
dest_dir  = "/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/raw"

print('\n ===== COPYTHING TO ', dest_dir, ' =====\n')
# make sure destination exists
os.makedirs(dest_dir, exist_ok=True)

with open(list_file, "r") as f:
    for line in f.readlines()[:]:
        line = line.replace('/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/raw', 'media/ttt/Extreme SSD/ADNI_1111/ADNIdcm')
        src = line.strip()
        if not src:        # skip empty lines
            continue
        if not os.path.isfile(src):
            print(f"Skipping (not found): {src}")
            continue

        filename = os.path.basename(src)
        dst = os.path.join(dest_dir, filename)

        print(f"Copying {src} -> {dst}")
        shutil.copy2(src, dst)  # copy2 keeps metadata


os.listdir(dest_dir)
with open("/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/input_0206.txt", "w", encoding="utf-8") as f:
    for nii in os.listdir(dest_dir):
        if '.nii' in nii:
            line = os.path.join(dest_dir, nii)
            f.write(f"{line}\n")  # ensures newline

os.listdir(dest_dir)
with open("/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/output_0206.txt", "w", encoding="utf-8") as f:
    for nii in os.listdir(dest_dir):
        if '.nii' in nii:
            line = os.path.join('/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/turboprep_out', nii.replace('.nii', ''))
            f.write(f"{line}\n")  # ensures newline


import os
import shutil
import subprocess
from pathlib import Path

input_file  = "/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/input_0206.txt"
output_file = "/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/output_0206.txt"

# Use no-space mount path everywhere (symlink)
input_file  = input_file.replace("Extreme SSD", "ExtremeSSD")
output_file = output_file.replace("Extreme SSD", "ExtremeSSD")

template = "/media/ttt/Extreme SSD/ADNI_1111/ADNI_0206/MNI152_T1_1mm_brain.nii"
template = template.replace("Extreme SSD", "ExtremeSSD")

# SSD final output root (exFAT)
ssd_out_root = "/media/ttt/ExtremeSSD/ADNI_1111/ADNI_0206/turboprep_out"
os.makedirs(ssd_out_root, exist_ok=True)

# Local staging root (Linux FS, safe for Docker chown)
local_stage_root = "/home/ttt/turboprep_stage"
os.makedirs(local_stage_root, exist_ok=True)

TURBOPREP = "/home/ttt/Desktop/turboprep/turboprep-docker"

def case_id_from_path(p: str) -> str:
    name = Path(p).name
    # handle .nii.gz nicely
    return name[:-7] if name.endswith(".nii.gz") else Path(p).stem

# IMPORTANT: output_file should be read mode "r" if it already exists with desired outputs
# (your original had "r", keeping it)
with open(input_file, "r", encoding="utf-8") as f_in, open(output_file, "r", encoding="utf-8") as f_out:
    for i, (in_line, out_line) in enumerate(zip(f_in, f_out), start=1):
        in_path = in_line.strip().replace("Extreme SSD", "ExtremeSSD")
        out_path_original = out_line.strip().replace("Extreme SSD", "ExtremeSSD")

        # skip empty lines
        if not in_path or not out_path_original:
            print(f"Skipping empty pair at line {i}")
            continue

        cid = case_id_from_path(out_path_original)

        # Final destination on SSD
        ssd_out_dir = os.path.join(ssd_out_root, cid)

        # Local staging destination (per-case)
        local_out_dir = os.path.join(local_stage_root, cid)

        # Skip if already processed on SSD
        if os.path.isdir(ssd_out_dir) and any(os.scandir(ssd_out_dir)):
            print(f"Skipping [{i}] already exists on SSD: {ssd_out_dir}")
            continue

        # Ensure fresh local staging dir
        if os.path.exists(local_out_dir):
            shutil.rmtree(local_out_dir)
        os.makedirs(local_out_dir, exist_ok=True)

        # Ensure SSD dir exists (even though exFAT chown is unsupported, mkdir is fine)
        os.makedirs(ssd_out_dir, exist_ok=True)

        # 1) Run turboprep writing to LOCAL
        cmd = [TURBOPREP, in_path, local_out_dir, template]
        print(f"Running [{i}]:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        # 2) Copy local -> SSD
        rsync_cmd = ["rsync", "-a", "--info=progress2", f"{local_out_dir}/", f"{ssd_out_dir}/"]
        print(f"Copying [{i}]:", " ".join(rsync_cmd))
        subprocess.run(rsync_cmd, check=True)

        # 3) Minimal verification then delete local
        if not any(os.scandir(ssd_out_dir)):
            raise RuntimeError(f"Copy verification failed for line {i}: {ssd_out_dir} is empty")

        shutil.rmtree(local_out_dir)
        print(f"Done [{i}] -> SSD and deleted local staging: {cid}")
