#!/usr/bin/env bash
# Initialize the batch starting point.
offset=0

# Initialize the batch size.
batch_size=999

# Define regular expression to validate batch.
batch="^[0-9]+"

# read in lines from post_ids_n.txt
while read -r line; do
    rank_math=$(vip @stanforddaily.preprod -- wp post meta get "$line" _primary_term_category)
    echo "echo y | vip @stanforddaily.production -- wp post meta update $line rank_math_primary_category $rank_math" >> categories-n.sh
done < post_ids_n.txt