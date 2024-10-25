import pandas as pd
import os
import re

def find_chromosome(genes):
    # Split the string by comma and strip spaces
    gene_list = [gene.strip() for gene in genes.split(',')]
    chromosomes = set()  # Use a set to avoid duplicates

    for gene in gene_list:
        for chromosome, genes in chr_gene_map.items():
            if gene in genes:
                chromosomes.add(chromosome)  # Add chromosome to set if gene is found

    return ', '.join(chromosomes) if chromosomes else '-'  # Return chromosomes or '-'

txt_folder = "project_jy database" # Define the folder containing blood group database

# Check if the folder exists
if not os.path.isdir(txt_folder):
    raise FileNotFoundError(f"Error: Folder '{txt_folder}' does not exist. Please check the folder path.")

# List all .txt files in the folder
txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]
if not txt_files:
    raise FileNotFoundError("Error: No .txt files found in the specified folder.")

combined_df = pd.DataFrame() # Create dataframe to store all information from each .txt file

# Extract file by file
for txt_file in txt_files:
    txt_path = os.path.join(txt_folder, txt_file)

    try:
        extracted_df = pd.read_csv(txt_path, delimiter="\t")
    except Exception as e:
        raise ValueError(f"Error reading '{txt_file}': {e}")

    try:
        # Using column index for extraction as some headers have inconsistent names
        cleaned_df = pd.DataFrame({
            'Blood_system' : extracted_df.iloc[:, 0],
            'Phenotype': extracted_df.iloc[:, 1],
            'Allele_name': extracted_df.iloc[:, 2],
            'GENE': extracted_df.iloc[:, 3],
            'Type' : extracted_df.iloc[:, 4],
            'Nucleotide_change' : extracted_df.iloc[:, 5],
            #'Amino_acid' : extracted_df.iloc[:, 6],
            #'Exon' : extracted_df.iloc[:, 7],
            #'Prevalence' : extracted_df.iloc[:, 8],
            #'Database' : extracted_df.iloc[:, 9],
            'hg38_position' : extracted_df.iloc[:, 10],
            'hg19_position' : extracted_df.iloc[:, 11],
            #'Comments' : extracted_df.iloc[:, 12]
            })
    except IndexError:
        raise IndexError(f"Error in '{txt_file}': Column indices do not match expected layout. Check column count.")

    combined_df = pd.concat([combined_df, cleaned_df], ignore_index=True)

combined_df = combined_df.fillna("-") # Fill empty cells with "-" 

# Each phenotype may be associated with > 1 SNP (therefore > 1 hg38_position and hg19_position)
# Split the string such that one row has only 1 nucleotide change, hg38_position and hg19_position
columns_to_explode = ['Nucleotide_change', 'hg38_position', 'hg19_position']
for col in columns_to_explode:
    combined_df[col] = combined_df[col].apply(lambda x: [s for s in re.split(r';+', x) if s])

# Find the maximum list length in each row across the specified columns
combined_df['max_len'] = combined_df[columns_to_explode].apply(lambda row: max(len(x) for x in row), axis=1)

# Pad each list to match the maximum length of that row for exploding
for col in columns_to_explode:
    combined_df[col] = combined_df.apply(lambda row: row[col] + ["-"] * (row['max_len'] - len(row[col])), axis=1)

combined_df = combined_df.explode(columns_to_explode).drop(columns='max_len').reset_index(drop=True)

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
    'X' : ['XG', 'XK', 'GATA1', 'CD99']
}

combined_df['Chromosome'] = combined_df['GENE'].apply(find_chromosome) # Add Chromosome number at last column
combined_df = combined_df.apply(lambda col: col.map(lambda x: x.lstrip() if isinstance(x, str) else x)) # Remove leading whitespace in every column 

# Save the combined_df into an excel
combined_df.to_excel('project_jy_tables.xlsx', index=False)
print("Done")