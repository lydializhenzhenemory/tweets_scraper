import os
import pandas as pd

# Directory where all text files are located
directory = '/Users/lydiali/Desktop/tweets_scraper/US_Election/tweets/2020-11/'

# List to store data
data = []

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(directory, filename)
        
        # Open and read each file
        with open(file_path, 'r') as file:
            content = file.read()
            data.append([filename, content])  # You can add more columns if needed

# Convert to DataFrame
df = pd.DataFrame(data, columns=['Filename', 'Content'])

# Save as CSV
df.to_csv('2020-11.csv', index=False)
