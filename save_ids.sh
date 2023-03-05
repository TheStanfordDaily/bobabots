# Initialize the batch starting point.
offset=0

# Initialize the batch size.
batch_size=999

# Define regular expression to validate batch.
batch="^[0-9]+"

while true; do
    # Get the IDs of the posts in the current batch.
    # This call only works if you have the VIP CLI installed and are an authenticated user.
    posts=$(vip @stanforddaily.preprod -- wp post list --field=ID --offset=$offset --posts_per_page=$batch_size)

    # If there are no posts in the current batch, exit the loop.
    if ! [[ $posts =~ $batch ]]; then
        break
    fi

    # Write post IDs to post_ids.txt
    for post in $posts; do
        rank_math=$(vip @stanforddaily.preprod -- wp post meta get "$post" _primary_term_category)
        echo "echo y | vip @stanforddaily.production -- wp post meta update $post rank_math_primary_category $rank_math" >> categories.sh
    done

    # Move to the next batch.
    offset=$((offset + batch_size))
done