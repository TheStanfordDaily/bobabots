# Read in post IDs from post_ids.txt
while read post_id; do
    echo "Post ID: $post_id"
    # vip @stanforddaily.develop -- wp post meta get $post_id _primary_term_category >> with_cats.txt &
    # Retrieve the _primary_term_category value for the post ID
    primary_term_category=$(vip @stanforddaily.develop -- wp post meta get $post_id _primary_term_category) &
    echo "Post ID: $post_id | Primary Term Category: $primary_term_category"

    # Write the post ID and _primary_term_category value to with_cats.txt
    # Remember to remove lines that have no _primary_term_category value
    echo "vip @stanforddaily.develop -- wp post meta update $post_id rank_math_primary_category $primary_term_category" >> with_cats.sh &
done < post_ids.txt