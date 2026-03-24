# PQTL-DIMPLE GWAS
This repository contains the analytical pipeline for the PQTL-DIMPLE GWAS project. The workflow is designed for the large-scale processing and harmonisation of proteomic summary statistics across three major cohorts:

UK Biobank (UKB-PPP): 2,940 protein summary statistics (pQTLs) as described in [(O’Donovan et al. (2023))](https://www.nature.com/articles/s41586-023-06592-6).

deCODE Genetics: 4,907 aptamers targeting 4,719 unique proteins, as reported in [(Ferkingstad et al. (2021))](https://www.nature.com/articles/s41588-021-00978-w#Sec14).

China Kadoorie Biobank (CKB): 2,923 Olink inflammation and cardiovascular traits accessible via [(CKB PheWeb)](https://pheweb.ckbiobank.org/).

# STEP1: Download UKB-PPP PQTL summary statistics from Synapse 
The UK Biobank Pharma Proteomics Project (UKB-PPP) represents a major collaboration between the UK Biobank and thirteen biopharmaceutical companies to characterize the plasma proteomic profiles of 54,219 participants. This effort involved comprehensive protein quantitative trait loci (pQTL) mapping of 2,940 aptamers corresponding to 2,923 proteins, identifying 14,287 primary genetic associations—85% of which were previously undiscovered. The project also included ancestry-specific pQTL mapping in non-European populations and identified independent secondary associations in 87% of cis and 30% of trans loci, significantly expanding the catalog of genetic instruments available for downstream genomic analyses [(Sun et al., 2023)](https://www.nature.com/articles/s41586-023-06592-6).

#### Install [synapseclient](https://python-docs.synapse.org/en/stable/tutorials/installation/)

```rust
pip install synapseclient
```

### European Data Download
To download the data, you must create an account on [(Synapse)](https://www.synapse.org/Home:x). Detailed instructions can be found [(here)]((docs/synapse.md))

```rust
mkdir -p /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_syn51365303/ 

nohup synapse get \
  --recursive \
  --downloadLocation /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_syn51365303/ \
  syn51365303 \
  > download_UKB-PPP_East_Asian_syn51365303.log 2>&1 &
```

A total of 2,940 files were downloaded and are stored in the directory: /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303. Each file is in a compressed .tar format and contains 23 chromosome-specific files (Autosomes 1–22 and Chromosome X).  Each of the 23 chromosome-specific files extracted from the .tar archives follows the standard GWAS summary statistics format shown below: 

| CHROM | GENPOS | ID | ALLELE0 | ALLELE1 | A1FREQ | INFO | N | TEST | BETA | SE | CHISQ | LOG10P | EXTRA |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 22 | 15285782 | 22:16692181:G:A:imp:v1 | G | A | 0.03373 | 0.75845 | 26225 | ADD | -0.04783 | 0.02461 | 3.77698 | 1.28431 | NA |
| 22 | 15324610 | 22:16653353:A:T:imp:v1 | A | T | 0.03270 | 0.85719 | 26225 | ADD | -0.05134 | 0.02350 | 4.77091 | 1.53843 | NA |
| 22 | 15328957 | 22:16649006:C:A:imp:v1 | C | A | 0.03291 | 0.87003 | 26225 | ADD | -0.05371 | 0.02326 | 5.33484 | 1.67979 | NA |
| 22 | 15335858 | 22:16642105:G:C:imp:v1 | G | C | 0.03283 | 0.91706 | 26225 | ADD | -0.05151 | 0.02268 | 5.15891 | 1.63587 | NA |
| 22 | 15336303 | 22:16641660:C:A:imp:v1 | C | A | 0.03311 | 0.92277 | 26225 | ADD | -0.05074 | 0.02252 | 5.07780 | 1.61557 | NA |
| 22 | 15336665 | 22:16641298:T:C:imp:v1 | T | C | 0.03305 | 0.92492 | 26225 | ADD | -0.05057 | 0.02251 | 5.04706 | 1.60787 | NA |
| 22 | 15340322 | 22:16637641:G:GT:imp:v1 | G | GT | 0.03382 | 0.97332 | 26225 | ADD | -0.04179 | 0.02170 | 3.70900 | 1.26664 | NA |
| 22 | 15345286 | 22:16632677:G:C:imp:v1 | G | C | 0.03005 | 0.93264 | 26225 | ADD | -0.04098 | 0.02347 | 3.04852 | 1.09253 | NA |
| 22 | 15348089 | 22:16629874:T:C:imp:v1 | T | C | 0.03382 | 1.00180 | 26225 | ADD | -0.04469 | 0.02139 | 4.36598 | 1.43577 | NA |

In the summary statistics files, the GENPOS column is mapped to the GRCh38 coordinate system; however, the variant ID column (formatted as CHR:POS:REF:ALT:imp:v1) utilizes the GRCh37 (hg19) positions.

### Metadata download

All metadata associated with the summary statistics files was downloaded from Synapse [(synapse)](https://www.synapse.org/Synapse:syn51396703). This file contains essential mapping and annotation details, including RSIDs and protein annotations for each protein in the UKB-PPP dataset

```rust

mkdir -p /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/ 

nohup synapse get \
  --recursive \
  --downloadLocation /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/ \
  syn51396703 \
  > download_UKB-PPP_East_Asian_syn51396703.log 2>&1 &

# Rename the folder
mv /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/'Protein annotation' /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/Protein_annotation
mv /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/'SNP RSID maps' /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/SNP_RSID_maps

```

Metadata File Locations
    
        Protein Annotations: /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/Protein_annotation/

        SNP RSID Maps: /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/SNP_RSID_maps/ 

Genome Build Clarification
"The gene positions (gene_start, gene_end) provided in the following metadata files are mapped to the GRCh38 coordinate system:

        /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/Protein_annotation/olink_protein_map_1.5k_v1.tsv
        /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/Metadata/Protein_annotation/olink_protein_map_3k_v1.tsv"

# STEP 2: Sumstat Extraction and Merging Chromosome wise files
The raw summary statistics are provided as compressed .tar archives. In this step, each protein pQTL sumstat archive is extracted into a folder containing chromosome-wise files (22 autosomes and the X chromosome). During this process, the pipeline performs automated integrity checks using tar and gzip to verify that no files are corrupted or truncated. These 23 individual files are then merged into a single, unified file.

The consolidated results are stored in the destination folder: `/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/`.

The Python script used for this process can be found [(here)](scripts/1_ukb_ppp_chrwise_sumstat_merging.py).

# STEP 3: Total Variant Count and Integrity Verification
In this step, the pipeline processes each merged summary statistic file to determine the total number of genetic variants. Since each file includes a header line, the total variant count is calculated as (total rows - 1).

Simultaneously, the script performs a final integrity check (using gzip -t) to ensure that no files were corrupted during the merging or saving processes. The results, including row counts and validation status, are saved to a central log for quality control.

The Python script used for this process can be found [(here)](scripts/2_merged_file_row_count.py). 

The comand used is below

```rust
nohup python \
    -u /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/2_merged_file_row_count.py > \
    /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/2_merged_file_row_count.log 2>&1 &
```

Output Locations:

        Analysis Results: /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/ukb-ppp_EUR_AllChr_merged_row_counts.csv

        Log File: /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/2_merged_file_row_count.log

Validation Summary:
All 2,940 merged summary statistic files were verified to ensure data integrity. Total variant counts across the dataset range from 12,493,868 to 16,053,405.

To confirm the accuracy of the automated pipeline, the four files with the lowest variant counts (representing Neurology, Cardiometabolic, and Inflammation II panels) were manually inspected using a [(validation script)](scripts/2b_variant_count_cnofirmation.sh). The manual counts perfectly match the automated results, confirming that the concatenation process was successful across all chromosomes. 

| Protein / Filename | Pipeline Count | Manual Count | Status |
| :--- | :--- | :--- | :--- |
| NPM1 (P06748_OID20961_v1_Neurology) | 12,493,868 | 12,493,868 | VALID |
| PCOLCE (Q15113_OID20384_v1_Cardiometabolic) | 13,332,767 | 13,332,767 | VALID |
| CTSS (P25774_OID21056_v1_Neurology) | 15,232,344 | 15,232,344 | VALID |
| CST1 (P01037_OID30581_v1_Inflammation_II) | 15,598,905 | 15,598,905 | VALID |

Manual count results can be found at : /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303/test/protein_counts.txt

# STEP 4: Harmonisation

This step automates the harmonization of merged UKB-PPP summary statistics using the postgwas [(harmonization module)](https://github.com/JIBINJOHNV/postgwas). During this process, each protein pQTL summary statistic is converted into VCF format for two different genome builds: GRCh37 and GRCh38.

The module also generates comprehensive Quality Control (QC) reports, providing metrics such as total variant counts, the number of variants successfully mapped to the VCF, variants meeting the INFO score > 0.7 threshold, and total SNP counts.

To manage the high computational demand of processing 2,940 protein summary statistics, the workload is split into parallel batches:

Master Mapping: Generates a unified input map linking raw summary statistics to the required genomic resources and metadata.

Data Sharding: Splits the master dataset into 10 independent chunks to facilitate horizontal scaling.

Dockerized Parallelism: Dispatches 10 simultaneous Docker containers, leveraging the server's high-memory capacity (995GB RAM) to significantly reduce total processing time.

The orchestration script for this parallel execution can be found [(here)](scripts/3_ukbb_ppp_sumstat_harmonisation.py).

```rust
nohup python \
    -u /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/2_merged_file_row_count.py > \
    /mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/2_merged_file_row_count.log 2>&1 &
```

### Harmonised Output Summary

Following the **PostGWAS** harmonisation of **2,940** summary statistics files, three distinct VCF outputs were generated for each dataset:

* **`_GRCh38_merged.vcf.gz`**: Variants mapped to original **GRCh38** coordinates.
* **`_GRCh37_merged.vcf.gz`**: Variants successfully lifted over to **GRCh37**.
* **`_GRCh37_notlifted_merged.vcf.gz`**: Variants that failed the **GRCh38 to GRCh37** liftover.

### Directory Structure

All harmonised output files are stored within the following root directory on the **Hillside/Ogawa** server:
`'/mnt/fast/Analysis/ukb-ppp_harmonisation/harmonised_vcf_files/'`

Each dataset is organized into a specific directory named after the protein or GWAS ID, with the final VCF files nested inside a `00_harmonised_sumstat/` subfolder.

**Example Path:**
```text
/mnt/fast/Analysis/ukb-ppp_harmonisation/harmonised_vcf_files/NARS1_O43776_OID31035_v1_Neurology_II/00_harmonised_sumstat/
```

# STEP 5: Post-Harmonisation Quality Control (QC)

In this step, a comprehensive summary is generated for the three VCF outputs (_GRCh38_merged, _GRCh37_merged, and GRCh37_notlifted) across all 2,940 harmonised datasets.

The summary statistics for each file include:

        Number of samples
        Number of SNPs
        Number of INDELs
        Number of MNPs
        Number of others
        Number of sites (Total variant count)

Validation & Data Integrity
Upon completion, the Number of sites from the _GRCh38_merged.vcf.gz files is cross-referenced against the QC file generated in STEP 3 (/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/ukb-ppp_EUR_AllChr_merged_row_counts.csv). This comparison is critical to identify and quantify any variant loss that may have occurred during the harmonisation process.

```rust
nohup python \
    -u /mnt/fast/Analysis/ukb-ppp_harmonisation/3ba_post_harmonisation_QC.py > \
    /mnt/fast/Analysis/ukb-ppp_harmonisation/3ba_post_harmonisation_QC.log 2>&1 & 

## check running or not 
 ps -ef | grep 3ba_post_harmonisation_QC.py
```

# STEP 6: Extract Z SCORE FROM Harmonised vcf files
For the [(DIMPLE-GWAS)](https://github.com/mlamcogent/DIMPLE-GWAS)  pipeline, we extract Z-scores from harmonized summary statistics for approximately 86,000 high-quality SNPs. These variants were derived from the HapMap reference panel following LD pruning ($R^2 < 0.1$) based on the 1000 Genomes European (EUR) population.  The script used in this step can be found [(here)](scripts/4a_prepare_z_sore_matrix.py).

```rust
nohup python \
    -u /mnt/fast/Analysis/ukb-ppp_harmonisation/4_prepare_z_sore_matrix.py > \
    /mnt/fast/Analysis/ukb-ppp_harmonisation/4_prepare_z_sore_matrix.log 2>&1 & 
```