# misc.py
from icecream import ic
import rarfile
import concurrent.futures as mps


class File:
    def __init__(self, file_path):
        self.file_path = file_path
        self.arj = rarfile.RarFile(file_path)

    @staticmethod
    def size(file_size):
        # file_size = self.file_path.stat().st_size
        # Format size based on value
        if file_size < (1024 * 1024):  # Less than 1 MB
            size = f"{file_size:.2f} KB"
        else:
            size = f"{file_size // (1024 * 1024):.2f} MB"

        return size

    def mask(self, filter=["*"]):
        with self.arj as arj:
            if filter == ["*"]:
                mask_files = arj.namelist()
            else:
                mask_files = [f for f in arj.namelist() if any(f.endswith(ft) for ft in filter)]

        return mask_files


if __name__ == "__main__":
    pass
