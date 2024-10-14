import pandas as pd
import pprint

def find_phenotypes_by_rs_number(phenotype_dict, rs_number):
    """
    Finds all phenotypes that have a matching rs number.

    Args:
        phenotype_dict (dict): The dictionary containing phenotype data.
        rs_number (str): The rs number to search for.

    Returns:
        list: A list of phenotypes that have a matching rs number.
    """

    matching_phenotypes = []
    for phenotype, alleles in phenotype_dict.items():
        for allele_name, details in alleles.items():
            # Check if the rs number matches
            if details['rs number'] == rs_number:
                matching_phenotypes.append(phenotype)
                # No break here, continue to check other alleles

    return matching_phenotypes

# Read Excel file
file_path = 'test_table_w_coordinate.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

# Load the Excel file
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"File not found: {file_path}")
    exit(1)
except KeyError as e:
    print(f"Missing expected column: {e}")
    exit(1)

# Create a dictionary from the DataFrame
phenotype_dict = {}
for index, row in df.iterrows():
    phenotype = row['Phenotype']
    allele_name = row['Allele name']
    nucleotide_change = row['Nucleotide change']
    rs_number = row['rs number']
    chromosome = str(row["Chromosome"])
    GRCh37_start = str(row["GRCH37 Start Coordinate"])
    GRCh37_end = str(row["GRCH37 End Coordinate"])
    GRCh38_start = str(row["GRCH38 Start Coordinate"])
    GRCh38_end = str(row["GRCH38 End Coordinate"])

    if phenotype not in phenotype_dict:
        phenotype_dict[phenotype] = {}
    phenotype_dict[phenotype][allele_name] = {'Nucleotide change': nucleotide_change, 'rs number' :rs_number, 'Chr' : chromosome, 'GRCh37 Start' : GRCh37_start, 'GRCh37 End' : GRCh37_end, 'GRCh38 Start' : GRCh38_start, 'GRCh38 End' : GRCh38_end}


# Example usage
rs_number_to_find = 'rs587777149' 

phenotype_results = find_phenotypes_by_rs_number(phenotype_dict, rs_number_to_find)

if phenotype_results:
    print(f"The phenotypes found for rs number {rs_number_to_find} are: {phenotype_results}")
else:
    print(f"No matching phenotypes found for rs number {rs_number_to_find}.")

# pprint.pprint(phenotype_dict) 