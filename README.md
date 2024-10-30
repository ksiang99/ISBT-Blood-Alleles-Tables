### **proj_jy_tables.py**
Combine text files from [reference database](https://github.com/xgao32/project_jy/tree/master/02_reference_database/db_genomeAnno) into 1 dataframe. File is unable to run on NUS HPC as function df.explode is not available in the older version of pandas.

### **Project_jy_Tables.xlsx**
Output of proj_jy_tables.py

# Ignore below

# ISBT Blood Alleles Tables

## **Files** 

### **download_links.txt**
Contains the download link for 44 blood group systems. CD36 and Transcription factors are not included.

### **download_ISBT_Table.py**
Scipt to download ISBT blood alleles tables.

### **Extract_ISBT_Table.py**
1. Converts ISBT blood alleles table in pdf into excel.
2. Cleans up the extracted tables.
3. Currently extracted 33/44 blood alleles tables (Though some columns still require cleaning)
4. Remaining 11 blood alleles tables are not extracted yet due to various table layout issues.

### **map_coordinates.py**
1. Extract GRCh37 and GRCh38 coordinates from **erythrogene_coordinate_fixed_with_chromosome.tsv** using matching gene and nucleotide change columns.
2. Alleles not in tsv file have their coordinates extracted from ensembl using rsID.
3. There is still a handful of alleles without coordinates.

### **infer_Phenotype.py** (Explanation is unclear for now)
1. Create a dictionary from ISBT blood alleles table excel.
2. Infer phenotype from vcf file based on
   i. Matching chrom and pos
   ii. Matching nucleotide changes
   iii. Homozygous will be reference allele of blood group, heterozygous will be the matched phenotype found
3. Current code only creates the dictionary. Have not tried the inference portion due to issues with libraries required to read vcf files.
