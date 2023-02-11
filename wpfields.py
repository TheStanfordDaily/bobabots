import os
import datetime
import subprocess

BATCH_SIZE = 9

def next_batch(offset):
    process = os.popen(f"vip @stanforddaily.develop -- wp post list --field=ID --offset={offset} --posts_per_page={BATCH_SIZE}")
    output = process.read()
    process.close()

    return output.strip().splitlines()

def all_post_ids():
    offset = 0
    batches = []
    while True:
        batch = next_batch(offset)
        if not batch or offset > 36:
            break
        batches.extend(batch)
        offset += BATCH_SIZE

    return batches

# print("Starting at", datetime.datetime.now())

# print(posts)
# print("Finished at", datetime.datetime.now())

def primary_term_categories(post_id):
    process = os.popen(f"vip @stanforddaily.develop -- wp post meta get {post_id} _primary_term_category")
    output = process.read()
    process.close()

    return output.strip().splitlines()

def all_primary_term_categories():
    posts = {x: "" for x in all_post_ids()}
    for post_id in posts.keys():
        posts[post_id] = primary_term_categories(post_id)

    return posts

print("Starting at", datetime.datetime.now())
print(all_primary_term_categories())
print("Finished at", datetime.datetime.now())