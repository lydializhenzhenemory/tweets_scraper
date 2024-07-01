import pandas as pd

# Read the dataset
df = pd.read_csv('2020-05.csv')

# Display the first few rows of the dataframe
print(df.head())

# Define the mapping from old headings to new headings
heading_mapping = {
    'status_id': 'id',
    'blacklivesmatter': 'created_at',  # Placeholder mapping, replace with actual intended mapping
    'alllivesmatter': 'attached_urls',  # Placeholder mapping, replace with actual intended mapping
    'bluelivesmatter': 'attached_urls2'  # Placeholder mapping, replace with actual intended mapping
}

# Rename the columns based on the mapping
df = df.rename(columns=heading_mapping)

# Add the missing columns with default values
additional_columns = [
    'attached_media', 'tagged_users', 'tagged_hashtags', 'favorite_count', 
    'bookmark_count', 'quote_count', 'reply_count', 'retweet_count', 'text', 
    'is_quote', 'is_retweet', 'language', 'user_id', 'source', 
    'views', 'poll', 'username', 'display_name', 'user_created_at', 'description', 
    'followers_count', 'friends_count', 'statuses_count', 'profile_image_url', 'verified'
]

for col in additional_columns:
    df[col] = None  # or set a default value if you have one

# Display the first few rows of the dataframe after renaming and adding columns
print(df.head())

# Save the processed dataframe to a new CSV file
df.to_csv('BLM_.csv', index=False)
