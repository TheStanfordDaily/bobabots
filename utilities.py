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
            if os.path.exists(file2):
                if os.path.getsize(file1) > os.path.getsize(file2):
                    print(f"File {file1} is already larger than {file2}. Keeping file.")
                elif os.path.getsize(file1) < os.path.getsize(file2):
                    print(f"File {file2} is larger than {file1}. Swapping.")
                    swap_files(file2, file1)

                # Otherwise, they are the exact same size. Do nothing.