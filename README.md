# ADNI_0206

This directory contains ADNI NIfTI scans, input/output path lists, and the outputs from a turboprep run.

## Contents
- Dataset dir structure.
<pre>
.
├── input_0206.txt
├── input.txt
├── MNI152_T1_1mm_brain.nii
├── output_0206.txt
├── output.txt
├── raw
    ├── XXX.nii
    └── ...
├── README.md
├── scripts
    ├── turboprep_postproc.py
    └── turboprep_preproc.py
└── turboprep_out
    └── ADNI_941_S_1311_MR_MPR__GradWarp_Br_20081026142330778_S56645_I123814
        ├── affine_transf.mat
        ├── normalized.nii.gz
        ├── mask.nii.gz
        └── segm.nii.gz
</pre>
- `raw/` original NIfTI inputs organized by subject/session folders.
- `turboprep_out/` per-scan output directories.
- `MNI152_T1_1mm_brain.nii` template volume file.
- `input.txt` input file paths for preprocessing. 1,735 total.
- `output.txt` output file paths for preprocessing.
- `input_0206.txt` runtime log of input file paths during preprocessing (identical to input.txt).
- `output_0206.txt` runtime log of output file paths during preprocessing (identical to output.txt).
- Check out dataset repo structure on Huggingface.
<pre>
python3 - <<'PY'
from huggingface_hub import HfApi
api = HfApi()
items = set()
for p in api.list_repo_files("nnuochen/ADNI", repo_type="dataset"):
    items.add(p.split("/", 1)[0])
for name in sorted(items):
    print(name)
PY
</pre>

## Structure of `turboprep_out`
- Contains 1,735 preprocessed sessions.
- Each session contains:
    - affine_transf.mat
    - mask.nii.gz
    - normalized.nii.gz
    - segm.nii.gz

## Post processing
- Normalize intensities to [-1, 1] where background is defined as -1. Normalization percentiles computed withn head masks.
- Foreground cropping and pad the volumes, masks, and segmentations to standardized shape: (160,192,160)
<pre>
python scripts/turboprep_postproc.py 
--root ./ADNI_0206/turboprep_out \
--outdir PATH/TO/OUTPUT/DST \
--n_samples ALL
</pre>
