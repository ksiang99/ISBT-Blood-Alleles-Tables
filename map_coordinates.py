
import pandas as pd
import re
import requests

# Extract variant GRCh37 and GRCh38 coordinates from Ensembl API
def get_variant_coordinates(rsid):
    # Ensembl server for REST API (GRCh38 by default)
    server = "https://rest.ensembl.org"
    
    # API endpoint for variant by rsID in GRCh38
    ext = f"/variation/human/{rsid}?"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Make request to Ensembl API for GRCh38 (default)
    response = requests.get(server + ext, headers=headers)
    if not response.ok:
        return None  # Return None if there's an error
    
    # Parse the JSON response for GRCh38
    decoded = response.json()
    coordinates = {
        'chromosome_grch38': None,
        'start_grch38': None,
        'end_grch38': None
    }
    
    if 'mappings' in decoded:
        for mapping in decoded['mappings']:
            if 'GRCh38' in mapping['assembly_name']:
                coordinates['chromosome_grch38'] = mapping['seq_region_name']
                coordinates['start_grch38'] = mapping['start']
                coordinates['end_grch38'] = mapping['end']
                break  # Get the first mapping only

    # Separate endpoint for GRCh37
    server_grch37 = "https://grch37.rest.ensembl.org"
    
    # API endpoint for variant by rsID in GRCh37
    ext_grch37 = f"/variation/human/{rsid}?"
    
    # Make request to Ensembl API for GRCh37
    response_grch37 = requests.get(server_grch37 + ext_grch37, headers=headers)
    if not response_grch37.ok:
        return coordinates  # Return coordinates with GRCh38 info if GRCh37 fails
    
    # Parse the JSON response for GRCh37
    decoded_grch37 = response_grch37.json()
    if 'mappings' in decoded_grch37:
        for mapping in decoded_grch37['mappings']:
            if 'GRCh37' in mapping['assembly_name']:
                coordinates['chromosome_grch37'] = mapping['seq_region_name']
                coordinates['start_grch37'] = mapping['start']
                coordinates['end_grch37'] = mapping['end']
                break  # Get the first mapping only

    return coordinates

# Read an Excel file
# Specify the sheet name if the file has multiple sheets, otherwise it will read the first sheet by default
excel_file_path = 'C:/Users/KS/Desktop/FYP_Code/1.xlsx'
df_excel = pd.read_excel(excel_file_path)

# Read a TSV file
tsv_file_path = 'C:/Users/KS/Desktop/FYP_Code/erythrogene_coordinate_fixed_with_chromosome.tsv'
df_tsv = pd.read_csv(tsv_file_path, sep='\t')

# Columns to copy from df_tsv
columns_to_copy = df_tsv.columns[-5:].astype(str)

# Iterate over rows in the Excel DataFrame
for index, row in df_excel.iterrows():
    nucleotide_change = row['nucleotide_change']
    gene = row['gene']

    # # Escape special characters for regex
    # nucleotide_change = re.escape(nucleotide_change)

    # Efficiently check for substring matches (disable regex in str.contains)
    matching_mask = df_tsv['Nucleotide Change'].str.contains(nucleotide_change, na=False, regex=False) | \
                   df_tsv.apply(lambda x: nucleotide_change in str(x['Nucleotide Change']), axis=1)

    # Apply gene condition
    matching_mask &= (df_tsv['Gene'] == gene)

    matching_rows = df_tsv[matching_mask]

    # If a match is found, copy the last 6 columns
    if not matching_rows.empty:
        # ... (Convert problematic column(s) in df_excel to 'object' dtype if needed)
        df_excel.loc[index, columns_to_copy] = matching_rows.iloc[0][columns_to_copy].values

# Before the loop where you update 'Chromosome':
df_excel['Chromosome'] = df_excel['Chromosome'].astype('object')

# Filter the DataFrame to only include rows where 'rs number' is not NaN and not 'NaN' string
valid_rsids_df = df_excel[(df_excel['rs_number'] != 'NaN') & (df_excel['GRCh37_Start'].isna())]

# Loop through the filtered DataFrame and get variant coordinates for each valid rsID
for idx, row in valid_rsids_df.iterrows():
    rsid = row['rs_number']
    coordinates = get_variant_coordinates(rsid)
    
    # Only update the DataFrame if coordinates are valid
    if coordinates:  # Check if coordinates is not None
        df_excel.at[idx, 'Chromosome'] = coordinates['chromosome_grch37'] or coordinates['chromosome_grch38']
        df_excel.at[idx, 'GRCh37_Start'] = coordinates['start_grch37']
        df_excel.at[idx, 'GRCh37_End'] = coordinates['end_grch37']
        df_excel.at[idx, 'GRCh38_Start'] = coordinates['start_grch38']
        df_excel.at[idx, 'GRCh38_End'] = coordinates['end_grch38']
    print(1)
# Save the updated Excel DataFrame to a new file
df_excel.to_excel("updated_excel_file1.xlsx", index=False)

print("Done")