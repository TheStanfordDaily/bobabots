# Initialize the batch starting point.
offset=0

# Initialize the batch size.
batch_size=999

# Define regular expression to validate batch.
batch="^[0-9]+"

while true; do
    # Get the IDs of the posts in the current batch.
    # This call only works if you have the VIP CLI installed and are an authenticated user.
    posts=$(vip @stanforddaily.develop -- wp post list --field=ID --offset=$offset --posts_per_page=$batch_size)
    
    # If there are no posts in the current batch, exit the loop.
    if ! [[ $posts =~ $batch ]]; then
        break
    fi

    # Write post IDs to post_ids_out.txt
    echo "$posts" >> post_ids_out.txt

    # Move to the next batch.
    offset=$((offset + batch_size))
done
