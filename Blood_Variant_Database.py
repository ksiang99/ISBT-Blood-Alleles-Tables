##--Problems to solve--##

# 1. Some alleles have no genetic coordinates even though they are not the reference allele.

# 2. Erthyrogene table has no phenotype and allele name data. Althought allele names are available in
# Erythrogene website, most are tagged with "1000G Only".

# 3. Eryhyrogene table is located at end of dataframe (Not sorted into project_jy table)

import pandas as pd
import numpy as np
import os
import re

# Chromosome to gene mapping
chr_gene_map = {
    '1' : ['RHD', 'RHCE', 'ACKR1', 'ERMAP', 'CD55', 'CR1', 'SMIM1'],
    '2' : ['GYPC', 'ABCB6'],
    '3' : ['B3GALNT1'],
    '4' : ['GYPA', 'GYPB', 'ABCG2', 'PIGG'],
    '6' : ['C4A', 'C4B', 'GCNT2', 'RHAG', 'SLC29A1'],
    '7' : ['ACHE', 'AQP1', 'KEL'],
    '9' : ['ABO', 'AQP3', 'GBGT1'],
    '11' : ['CD44', 'CD151', 'CD59'],
    '12' : ['ART4'],
    '13' : ['ABCC4'],
    '15' : ['SEMA7A'],
    '17' : ['SLC4A1', 'B4GALNT2'],
    '18' : ['SLC14A1'],
    '19' : ['BCAM', 'FUT3', 'ICAM4', 'FUT1', 'FUT2', 'BSG', 'KLF1', 'SLC44A2', 'EMP3'],
    '20' : ['PRNP'],
    '22' : ['A4GALT'],
    '23' : ['XG', 'XK', 'GATA1', 'CD99']
}

# Function to assign chromosome for each row in dataframe
def assign_chr(genes):
    gene_list = [gene.strip() for gene in genes.split(',')]
    chromosomes = set()

    for gene in gene_list:
        for chromosome, genes in chr_gene_map.items():
            if gene in genes:
                chromosomes.add(chromosome)

    return ', '.join(chromosomes) if chromosomes else '-'

# Function to extract numeric coordinates
def extract_numeric(pos):
    if pos == '-':
        return '-'
    return re.sub(r'(_.*|-.*|>.*|\D)', '', pos) 

# Function to clean dataframe
def clean_df(combined_df):
    combined_df = combined_df.replace(np.nan, "-")
    
    # Each phenotype may be associated with > 1 SNP. Split the string such that one row has only 1 nucleotide change, hg38_position and hg19_position
    columns_to_explode = [combined_df.columns[5], combined_df.columns[6], combined_df.columns[7]]
    for col in columns_to_explode:
        combined_df[col] = combined_df[col].apply(lambda x: [s for s in re.split(r';+', x) if s])

    # Find the maximum list length in each row across the specified columns
    combined_df['max_len'] = combined_df[columns_to_explode].apply(lambda row: max(len(x) for x in row), axis=1)

    # Pad each list to match the maximum length of that row for exploding
    for col in columns_to_explode:
        combined_df[col] = combined_df.apply(lambda row: row[col] + ["-"] * (row['max_len'] - len(row[col])), axis=1)

    combined_df = combined_df.explode(columns_to_explode).drop(columns='max_len').reset_index(drop=True)

    # Add Chromosome number at last column
    combined_df['Chromosome'] = combined_df['Gene'].apply(assign_chr) 
    combined_df = combined_df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    # Extract numeric coordinates
    combined_df['GRCh38_Start'] = combined_df['GRCh38 Coordinates'].apply(extract_numeric)
    combined_df['GRCh37_Start'] = combined_df['GRCh37 Coordinates'].apply(extract_numeric)
    combined_df = combined_df.fillna("-")
    
    return combined_df

# Function to include variants_to_keep not found in dataframe
def add_missing_var(cleaned_df, erythro_df, keep_var_file):
    with open(keep_var_file, 'r') as f:
        keep_var = [line.strip() for line in f if line.strip()]

    for i in keep_var:
        check_chr = False
        chr, pos = i.split(":")
        pos_match = cleaned_df[cleaned_df['GRCh37_Start'] == pos]
        if pos_match.empty:
            check_chr = True
        else:
            if not (pos_match["Chromosome"] == chr).any():
                check_chr = True
        
        if check_chr:
                erythro_row = erythro_df[(erythro_df['GRCh37_Start'].astype(str).str.contains(pos, na=False))]
                if not erythro_row.empty:
                    erythro_row = erythro_row.drop(columns=['GRCh37_End', 'GRCh38_End'], errors='ignore')
                    cleaned_df = pd.concat([cleaned_df, erythro_row], ignore_index=True)

    return cleaned_df

##--Main Script--##

# Set file paths
txt_folder = "project_jy database"
txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
erythro_file = "erythrogene_coordinate_fixed_with_chromosome.tsv"
keep_var_file = "grch37_variants_to_keep.txt"

# Create dataframes
combined_df = pd.DataFrame()
erythro_df = pd.read_csv(erythro_file, delimiter="\t")
erythro_df = erythro_df.astype(str)
erythro_df.columns = erythro_df.columns.str.rstrip()
erythro_df = erythro_df.applymap(lambda x: x.rstrip() if isinstance(x, str) else x)

# Combine all text files into 1 dataframe
for txt_file in txt_files:
    txt_path = os.path.join(txt_folder, txt_file)
    try:
        extracted_df = pd.read_csv(txt_path, delimiter="\t")
    except Exception as e:
        raise ValueError(f"Error reading '{txt_file}': {e}")

    try:
        # Using column index for extraction as some headers have inconsistent names
        temp_df = pd.DataFrame({
            'Blood System' : extracted_df.iloc[:, 0],
            'Phenotype': extracted_df.iloc[:, 1],
            'Allele Name': extracted_df.iloc[:, 2],
            'Gene': extracted_df.iloc[:, 3],
            'Variant_Type' : extracted_df.iloc[:, 4],
            'Nucleotide Change' : extracted_df.iloc[:, 5],
            #'Amino_acid' : extracted_df.iloc[:, 6],
            #'Exon' : extracted_df.iloc[:, 7],
            #'Prevalence' : extracted_df.iloc[:, 8],
            #'Database' : extracted_df.iloc[:, 9],
            'GRCh38 Coordinates' : extracted_df.iloc[:, 10],
            'GRCh37 Coordinates' : extracted_df.iloc[:, 11],
            #'Comments' : extracted_df.iloc[:, 12]
            })
    except IndexError:
        raise IndexError(f"Error in '{txt_file}': Column indices do not match expected layout. Check column count.")

    # Sort data such that reference allele is at the top
    temp_df = temp_df.replace("-", np.nan)
    temp_df = temp_df.fillna(np.nan)
    nan_rows = temp_df[temp_df['GRCh37 Coordinates'].isna()]
    non_nan_rows = temp_df[~temp_df['GRCh37 Coordinates'].isna()]
    sorted_df = pd.concat([nan_rows, non_nan_rows])
    sorted_df = sorted_df.reset_index(drop=True)
    combined_df = pd.concat([combined_df, sorted_df], ignore_index=True)

cleaned_df = clean_df(combined_df)
cleaned_df = cleaned_df.astype(str)
cleaned_df.to_excel('project_jy_tables.xlsx', index=False)
cleaned_df.to_csv('project_jy_tables.tsv', sep='\t', index=False)

final_df = add_missing_var(cleaned_df, erythro_df, keep_var_file)
final_df = final_df.fillna("<Placeholder>")
final_df.to_excel('Blood_Variant_Database.xlsx', index=False)
final_df.to_csv('Blood_Variant_Database.tsv', sep='\t', index=False)

print("Done")