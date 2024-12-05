import pandas as pd

# Define file paths
jy_file = "project_jy_tables.tsv"
erythro_file = "erythrogene_coordinate_fixed_with_chromosome.tsv"

# Create dataframes, set all values to string and create a new column Chr num:GRCh37 coordinate
jy_df = pd.read_csv(jy_file, delimiter="\t")
jy_df = jy_df.astype(str)
jy_df['Chr:GRCh37'] = jy_df['Chromosome'] + ':' + jy_df['GRCh37_Start']

erythro_df = pd.read_csv(erythro_file, delimiter="\t")
erythro_df = erythro_df.astype(str)
erythro_df.columns = erythro_df.columns.str.rstrip()
erythro_df = erythro_df.apply(lambda col: col.map(lambda x: x.rstrip() if isinstance(x, str) else x))
erythro_df['Chr:GRCh37'] = erythro_df['Chromosome'] + ':' + erythro_df['GRCh37_Start']

# Drop reference variant
jy = jy_df[~jy_df['Chr:GRCh37'].str.contains('-')]

# Use set to drop duplicates and find variant exclusive to jy and erythro
jy_set = set(jy['Chr:GRCh37'])
erythro_set = set(erythro_df['Chr:GRCh37'])
jy_exclusive = jy_set - erythro_set
erythro_exclusive = erythro_set - jy_set
common_variant = jy_set & erythro_set

# Convert the set to a DataFrame to save as txt files
jy_exclusive_df = pd.DataFrame(jy_exclusive)
erythro_exclusive_df = pd.DataFrame(erythro_exclusive)
common_variant_df = pd.DataFrame(common_variant)

jy_exclusive_df.to_csv('jy_variants.txt', index=False, header=False)
erythro_exclusive_df.to_csv('erythro_variants.txt', index=False, header=False)
common_variant_df.to_csv('common_variants.txt', index=False, header=False)

print("Done")