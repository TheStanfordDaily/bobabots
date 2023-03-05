import os

def swap_files(file1, file2):
    if os.path.exists(file2):
        os.rename(file1, file2 + ".tmp")
        os.rename(file2, file1)
        os.rename(file2 + ".tmp", file2)


# Compare folders with files in another folder that contains files with the same names.
# Identify which file is larger for each pair; swap if necessary.
def compare_folders(path1, path2):
    for filename in os.listdir(path1):
        if filename.endswith(".html"):
            file1 = os.path.join(path1, filename)
            file2 = os.path.join(path2, filename)
            if os.path.exists(file2) and os.path.getsize(file1) < os.path.getsize(file2):
                # File 2 is larger than File 1. Swapping.
                swap_files(file2, file1)


def load_env() -> tuple:
    pairs = {}
    with open(os.path.join(os.path.dirname(__file__), ".env")) as f:
        for line in f:
            key, value = line.split("=")
            pairs[key] = value.strip().replace('"', "")

    if "CLIENT_KEY" not in pairs or "CLIENT_SECRET" not in pairs:
        raise Exception("No CLIENT_KEY or CLIENT_SECRET in .env")

    return pairs["CLIENT_KEY"], pairs["CLIENT_SECRET"]
