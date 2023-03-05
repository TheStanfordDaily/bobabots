import os
import re


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


def shell_script_append(path_in, path_out):
    valid_line = r"echo y \| vip @stanforddaily\.production -- wp post meta update \d+ rank_math_primary_category \d+"
    with open(path_in) as file_in:
        valid_lines = [x.strip() for x in file_in.readlines() if re.match(valid_line, x.strip())]
    with open(path_out, "a") as file_out:
        for index, line in enumerate(valid_lines):
            file_out.write(line + " &\n")
            if index % 4 == 0:
                file_out.write("wait")
            file_out.write("\n")
