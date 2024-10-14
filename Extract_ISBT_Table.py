
import tabula
import pandas as pd
import os
import requests
import re

# Keep the first name of phenotype and remove the rest
def clean_phenotype(value):
    if isinstance(value, str):
        # Remove specified patterns and trim whitespace
        value = re.sub(r'ER:.*|WLF.*|,.*|or.*|AUG:.*', '', value)
        value = value.strip()  # Remove leading/trailing spaces
    return value

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

# Specify the folder containing the PDF files
pdf_folder = "C:/Users/KS/Desktop/Code for FYP/ISBT Blood Alleles Table/"

# Get a list of all PDF files in the specified folder
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]  # Ensure we only process PDF files

# Initialize an empty DataFrame to hold all tables
all_tables_df = pd.DataFrame()

# Loop through each PDF file
for pdf_file in pdf_files:
    pdf_path = os.path.join(pdf_folder, pdf_file)  # Get the full path

    # Extract tables from page 2 of the PDF
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Concatenate all extracted tables into one DataFrame
    if tables:
        concatenated_df = pd.concat(tables, ignore_index=True)

        # Specify columns to keep
        columns_indices_to_keep = [0, 1, 2, 7]  # 0 is phenotype, 1 is allele name, 2 is nucleotide change, 7 is rs number

        # Use .iloc to keep only the specified columns
        concatenated_df = concatenated_df.iloc[:, columns_indices_to_keep]

        # Remove empty rows (rows where all elements are NaN)
        concatenated_df = concatenated_df.dropna(how='all')

        # Apply the cleaning function to the Phenotype column
        if 'Phenotype' in concatenated_df.columns:
            concatenated_df["Phenotype"] = concatenated_df["Phenotype"].apply(clean_phenotype)

        # Append the concatenated DataFrame to the main DataFrame
        all_tables_df = pd.concat([all_tables_df, concatenated_df], ignore_index=True)

# Fill 'Nucleotide change' with 'Reference' where NaN
all_tables_df['Nucleotide change'] = all_tables_df['Nucleotide change'].fillna('Reference')

# Remove unwanted rows based on specific keywords
all_tables_df = all_tables_df[~all_tables_df.apply(
    lambda row: row.astype(str).str.contains("Null phenotypes|Altered phenotypes|Null alleles|Null Phenotypes|Null phenotype").any(), axis=1
)]

# Clean up 'Allele name' and 'rs number' columns
if 'Allele name' in all_tables_df.columns:
    all_tables_df["Allele name"] = all_tables_df["Allele name"].replace(r'\s*or\s*.*|†.*|‡.*', '', regex=True).str.strip()
   
if 'rs number' in all_tables_df.columns:
    all_tables_df["rs number"] = all_tables_df["rs number"].replace({'n.a.': 'NaN', 'N/A': 'NaN'})
    all_tables_df["rs number"] = all_tables_df["rs number"].fillna('NaN')

# Add new columns for coordinates
all_tables_df[['Chromosome', 'GRCH37 Start Coordinate', 'GRCH37 End Coordinate', 'GRCH38 Start Coordinate', 'GRCH38 End Coordinate']] = None

# Filter the DataFrame to only include rows where 'rs number' is not NaN and not 'NaN' string
valid_rsids_df = all_tables_df[all_tables_df['rs number'].notna() & (all_tables_df['rs number'] != 'NaN')]

# Loop through the filtered DataFrame and get variant coordinates for each valid rsID
for idx, row in valid_rsids_df.iterrows():
    rsid = row['rs number']
    coordinates = get_variant_coordinates(rsid)
    
    # Only update the DataFrame if coordinates are valid
    if coordinates:  # Check if coordinates is not None
        all_tables_df.at[idx, 'Chromosome'] = coordinates['chromosome_grch37'] or coordinates['chromosome_grch38']
        all_tables_df.at[idx, 'GRCH37 Start Coordinate'] = coordinates['start_grch37']
        all_tables_df.at[idx, 'GRCH37 End Coordinate'] = coordinates['end_grch37']
        all_tables_df.at[idx, 'GRCH38 Start Coordinate'] = coordinates['start_grch38']
        all_tables_df.at[idx, 'GRCH38 End Coordinate'] = coordinates['end_grch38']

# Save the concatenated DataFrame to an Excel file
output_excel = "abc.xlsx"
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    all_tables_df.to_excel(writer, sheet_name='All_Tables', index=False)

print(f"All tables from pages with first 3 columns (excluding rows with 'Null phenotypes' or 'Altered phenotypes'), "
      f"with asterisk removal and multiline handling in the third column, have been successfully saved to {output_excel}")