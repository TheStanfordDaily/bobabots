import os
from tqdm import tqdm


def populate_rank_math_categories(post_ids: list[str]):
    for post_id in tqdm(post_ids):
        p1 = os.popen(f"vip @stanforddaily.develop -- wp post meta get {post_id} _primary_term_category")
        category = p1.read().strip()
        p1.close()

        if len(category) > 0:
            p2 = os.popen(f"vip @stanforddaily.develop -- wp post meta update {post_id} rank_math_primary_category {category}")
            p2.read()
            p2.close()
            print(f"Successfully updated {post_id} with {category}")


if __name__ == "__main__":
    with open("post_ids.txt") as f:
        lines = [x.strip() for x in f.readlines()]
    populate_rank_math_categories(lines)
