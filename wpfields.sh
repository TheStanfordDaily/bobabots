# Initialize the batch starting point
offset=0

# Initialize the batch size
batch_size=999
digit="^[0-9]+$"
batch="^[0-9]+"

while true; do
    # Get the IDs of the posts in the current batch
    posts=$(vip @stanforddaily.preprod -- wp post list --field=ID --offset=$offset --posts_per_page=$batch_size)
  
    # If there are no posts in the current batch, exit the loop
    if ! [[ $posts =~ $batch ]]; then
        break
    fi

    echo "Processing posts $offset to $((offset + batch_size))"

    # Loop through each post in the current batch
    for post in $posts; do
        # Get the value of the `primary_term_category` field for the current post
        echo "Processing post ID $post"
        primary_term_category=$(vip @stanforddaily.preprod -- wp post meta get $post _primary_term_category)
        
        # Check against re
        if ! [[ $primary_term_category =~ $digit ]]; then
            # If the `primary_term_category` field is empty, skip to the next post
            continue
        fi

        # Update the `rank_math_primary_category` field for the current post
        vip @stanforddaily.preprod -- wp post meta update $post rank_math_primary_category $primary_term_category
    done

    # Move to the next batch
    offset=$((offset + batch_size))
done