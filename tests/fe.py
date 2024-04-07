from icecream import ic
import rarfile
from pathlib import Path

ROOT = Path().cwd()
FDIR = ROOT / "files"
FILE = FDIR / "ar_400_mb.rar"
TMP = ROOT / "tmp"


def extract_with_progress(fpath, fdist, ext=["*"]):
    with rarfile.RarFile(fpath) as rf:
        files_to_extract = [f for f in rf.infolist() if any(f.filename.endswith(e) for e in ext) or "*" in ext]
        total_files = len(files_to_extract)
        for i, part in enumerate(files_to_extract, start=1):
            rf.extract(part, fdist)
            ic(part.filename)
            print(f"Extraction progress: {i/total_files*100:.2f}%")

        print("Extraction completed.")


extract_with_progress(FILE, TMP, ext=["txt"])
