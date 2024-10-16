import tabula
import pandas as pd
import os
import re

# Normalize column names for easier matching
def normalize_column_name(col):
    return re.sub(r'\s+', '_', col.strip().lower())

# Keep the first name of phenotype and remove the rest
def clean_phenotype(value):
    if isinstance(value, str):
        # Remove specified patterns and trim whitespace
        value = re.sub(r'ER:.*|or.*|†.*|comment.*|erythroid.*', '', value)
        value = value.strip()
    return value

# A list of gene to create a column
gene = ["A4GALT", "BCAM", "ACKR1", "SLC14A1", "SLC4A1", "ACHE", "ERMAP", "AQP1",
        "ICAM4", "CH(C4B)^", "XK", "CD55", "CD44", "OK^", "CD151", "SEMA7A",
        "GCNT2", "AQP3", "RHAG", "GBGT1", "ABCG2", "ABCB6", "SMIM1",
        "CD59", "SLC29A1", "PRNP^", "B4GALNT2^", "CTL2^", "SLC44A2^",
        "ABCC4^", "EMP3^", "PIGG^", "ABCC1^", "PIEZO1^"]


pdf_folder = "C:/Users/KS/Desktop/FYP_Code/ISBT Blood Alleles Table/"
pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
all_tables_df = pd.DataFrame()

for i, pdf_file in enumerate(pdf_files):
    pdf_path = os.path.join(pdf_folder, pdf_file)
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Concatenate all extracted tables into one DataFrame
    if tables:
        concatenated_df = pd.concat(tables, ignore_index=True)

        # Normalize column names
        normalized_columns = {col: normalize_column_name(col) for col in concatenated_df.columns}
        concatenated_df.rename(columns=normalized_columns, inplace=True)

        # Identify columns that may contain variations of "Allele name", and "rs number"
        allele_cols = [col for col in concatenated_df.columns if 'allele_name' in col.lower()]
        rsID_cols = [col for col in concatenated_df.columns if 'rs_number' in col.lower()]

        # Rename nucleotide change and phenotype columns to 'nucleotide_change' and 'phenotype' respectively
        for col in concatenated_df.columns:
            if 'nucleotide_change' in col.lower():
                normalized_columns[col] = 'nucleotide_change'
            elif 'phenotype' in col.lower():
                normalized_columns[col] = 'phenotype'
    
        # Apply the renaming to the DataFrame
        concatenated_df.rename(columns=normalized_columns, inplace=True)
        
        # Specify columns to keep
        columns_to_keep = ['phenotype'] + allele_cols + ['nucleotide_change'] + rsID_cols
        
        # Use the column names to filter the DataFrame
        concatenated_df = concatenated_df[columns_to_keep]

        # Insert gene for the blood alleles
        concatenated_df.insert(0, 'gene', gene[i])

        if 'rs_number' in concatenated_df.columns:
            concatenated_df["rs_number"] = concatenated_df["rs_number"].fillna('NaN')

        # Remove empty rows and columns
        concatenated_df = concatenated_df.dropna(how='all')
        desired_num_columns = len(columns_to_keep) + 1
        concatenated_df = concatenated_df[concatenated_df.notnull().sum(axis=1) >= desired_num_columns - 1]
        concatenated_df = concatenated_df.dropna(axis=1,how='all')
        
        # Append the concatenated DataFrame to the main DataFrame
        all_tables_df = pd.concat([all_tables_df, concatenated_df], ignore_index=True)

        print(f'Processed {pdf_file}')

## Clean up 'Nucleotide change' column

# Fill empty cells with 'Reference'
all_tables_df['nucleotide_change'] = all_tables_df['nucleotide_change'].fillna('Reference')

# Split the information and create separate rows for each nucleotide change. 'Phenotype' and 'allele name' will be empty.
all_tables_df['nucleotide_change'] = all_tables_df['nucleotide_change'].str.split(';')
all_tables_df = all_tables_df.explode('nucleotide_change')
all_tables_df['nucleotide_change'] = all_tables_df['nucleotide_change'].str.split(r'(?:\s|^)(?=\(?c\.)')
all_tables_df = all_tables_df.explode('nucleotide_change')

# Remove rows with empty cells after explode
all_tables_df = all_tables_df[all_tables_df['nucleotide_change'] != '']

# Add "c." to nucleotide changes that start with a number if "c." is not present
all_tables_df['nucleotide_change'] = all_tables_df['nucleotide_change'].apply(
lambda x: 'c.' + x if x[0].isdigit() and not x.startswith('c.') else x)

## Fill the empty rows of "phenotype" and "allele name" columns with the previous row values
all_tables_df['phenotype'] = all_tables_df['phenotype'].ffill()
all_tables_df['allele_name'] = all_tables_df['allele_name'].ffill()

## Clean up "Phenotype" column
if 'phenotype' in all_tables_df.columns:
    all_tables_df["phenotype"] = all_tables_df["phenotype"].apply(clean_phenotype)

# Clean up 'Allele name column
if 'allele_name' in all_tables_df.columns:
    all_tables_df["allele_name"] = all_tables_df["allele_name"].replace(r'\s*or\s*.*|†.*|‡.*', '', regex=True).str.strip()

# Save the concatenated DataFrame to an Excel file
output_excel = "1.xlsx"
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    all_tables_df.to_excel(writer, sheet_name='All_Tables', index=False)

print("Done")