import pandas as pd

# Load the datasets
df1 = pd.read_csv('BLM.csv')
df2 = pd.read_csv('BLM_.csv')

# Ensure the 'id' columns are of the same data type
df1['id'] = df1['id'].astype(str)
df2['id'] = df2['id'].astype(str)

# Merge the datasets based on the 'id' column using an outer join
merged_df = pd.merge(df2, df1, on='id', how='outer', suffixes=('_df2', '_df1'))

# Resolve column conflicts
for column in df1.columns:
    if column in df2.columns and column != 'id':
        merged_df[column] = merged_df[column + '_df2'].combine_first(merged_df[column + '_df1'])
        merged_df.drop(columns=[column + '_df2', column + '_df1'], inplace=True)
    elif column not in df2.columns:
        merged_df[column] = merged_df[column + '_df1']
        merged_df.drop(columns=[column + '_df1'], inplace=True)

# Save the merged dataset to a new CSV file
merged_df.to_csv('merged_BLM.csv', index=False)

print("Merged dataset saved successfully.")
