# ISBT Blood Alleles Tables

## **Files** 

### **download_links.txt**
Contains the download link for 44 blood group systems. CD36 and Transcription factors are not included.

### **download_ISBT_Table.py**
Scipt to download ISBT blood alleles tables.

### **Extract_ISBT_Table.py**
1. Converts ISBT blood alleles table in pdf into excel.
2. Cleans up the extracted tables.
3. Extract GRCh37 and GRCh38 coordinates from ensembl using rsID. (Need to use erythrogene_coordinate.tsv to get coordinates instead)
4. Currently only tested extraction for blood group system RAPH (no.25) to ER (no.44).

### **infer_Phenotype.py** (Explanation is unclear for now)
1. Create a dictionary from ISBT blood alleles table excel.
2. Infer phenotype from vcf file based on
   i. Matching chrom and pos
   ii. Matching nucleotide changes
   iii. Homozygous will be reference allele of blood group, heterozygous will be the matched phenotype found
3. Current code only creates the dictionary. Have not tried the inference portion due to issues with libraries required to read vcf files.
