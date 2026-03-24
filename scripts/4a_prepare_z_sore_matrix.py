import os
import glob
import logging
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor


# --- 1. CONFIGURATION & PATHS ---
BASE_DIR = Path('/mnt/fast/Analysis/ukb-ppp_harmonisation/')
RESOURCE_DIR = Path('/mnt/fast/Resourses/dimple_gwas/')
Z_MATRIX_DIR = BASE_DIR / 'ukb-ppp_zscore_matrix'

# CRITICAL: Create the directory BEFORE the logger tries to write to it
Z_MATRIX_DIR.mkdir(parents=True, exist_ok=True)

# Input resource from GCS
HAPMAP_GCS = "gs://software_resourse/dimple_gwas/hapmap_snp_GRCh37_R0.1_R0.6_.tsv"
HAPMAP_RAW = RESOURCE_DIR / "hapmap_snp_GRCh37_R0.1_R0.6_.tsv"
HAPMAP_SORTED = RESOURCE_DIR / "hapmap_snp_GRCh37_R0.1_sorted.tsv.gz"

# Logging & Audit Files
LOG_FILE = Z_MATRIX_DIR / f"zscore_extraction_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
AUDIT_REPORT = Z_MATRIX_DIR / "zscore_extraction_audit_report.tsv"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)


# --- 2. UTILITY FUNCTIONS ---
def run_shell(cmd):
    """Executes a shell command and returns (success_boolean, error_message)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, ""


def prepare_environment():
    """Missing section: Downloads resources, filters HapMap, sorts, and indexes."""
    logging.info("Step 1: Preparing directories and resources...")
    Z_MATRIX_DIR.mkdir(parents=True, exist_ok=True)
    RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    # Download from Google Cloud if missing
    if not HAPMAP_RAW.exists():
        logging.info(f"Downloading {HAPMAP_RAW.name}...")
        success, err = run_shell(f'gsutil -m cp "{HAPMAP_GCS}" {RESOURCE_DIR}/')
        if not success: raise RuntimeError(f"GCS Download failed: {err}")
    # Process and Filter HapMap (R2 >= 0.1)
    if not HAPMAP_SORTED.exists():
        logging.info("Filtering and Indexing HapMap SNPs...")
        temp_tsv = RESOURCE_DIR / "temp_hapmap_filtered.tsv"
        # Pandas filtering logic
        df = pd.read_csv(HAPMAP_RAW, sep="\t")
        df_filtered = df[df['R2_0.1'].notna()].sort_values(["CHROM", "POS"]).iloc[:, 0:4]
        df_filtered.to_csv(temp_tsv, index=None, sep="\t", header=None)
        # Sort, Bgzip, and Tabix
        cmd = (
            f"sort -k1,1 -k2,2n {temp_tsv} | bgzip -c > {HAPMAP_SORTED} && "
            f"tabix -f -s1 -b2 -e2 {HAPMAP_SORTED}"
        )
        success, err = run_shell(cmd)
        if temp_tsv.exists(): temp_tsv.unlink() # Cleanup
        if not success: raise RuntimeError(f"Indexing failed: {err}")
    logging.info("Environment preparation complete.")

def extract_zscore(vcf_file):
    """Worker function for parallel extraction of Z-scores."""
    vcf_path = Path(vcf_file)
    sample_name = vcf_path.parts[-3] 
    output_file = Z_MATRIX_DIR / f"{sample_name}_zscore.tsv"
    try:
        if output_file.exists():
            return (sample_name, "SKIPPED", "Output file already exists.")
        header = f"CHROM\tPOS\tID\tREF\tALT\t{sample_name}"
        # Command uses double-backslashes for Python string -> Shell escape
        cmd = (
            f'echo "{header}" > {output_file} && '
            f'bcftools view -T {HAPMAP_SORTED} {vcf_path} | '
            f'bcftools query -f "%CHROM\\t%POS\\t%ID\\t%REF\\t%ALT\\t[%EZ]\\n" >> {output_file}'
        )
        success, err_msg = run_shell(cmd)
        if success:
            return (sample_name, "SUCCESS", "Processed successfully")
        else:
            if output_file.exists(): output_file.unlink() # Delete corrupt file
            return (sample_name, "FAILED", f"BCFtools error: {err_msg}")
    except Exception as e:
        return (sample_name, "CRITICAL_ERROR", str(e))

# --- 3. MAIN EXECUTION ---

if __name__ == "__main__":
    try:
        prepare_environment()

        # Find VCF files
        search_pattern = str(BASE_DIR / "harmonised_vcf_files" / "*" / "00_harmonised_sumstat" / "*_GRCh37_merged.vcf.gz")
        vcf_files = glob.glob(search_pattern)
        
        if not vcf_files:
            logging.error("No VCF files found. Check your search pattern.")
            exit(1)

        logging.info(f"Found {len(vcf_files)} samples. Starting Parallel extraction...")

        # Parallel Pool
        with ProcessPoolExecutor(max_workers=12) as executor:
            results = list(executor.map(extract_zscore, vcf_files))

        # Generate Audit Report (Always created)
        report_df = pd.DataFrame(results, columns=["Sample_ID", "Status", "Message"])
        report_df.to_csv(AUDIT_REPORT, sep="\t", index=False)
        
        logging.info(f"Audit report saved to: {AUDIT_REPORT}")
        logging.info("Pipeline Execution Finished.")

    except Exception as e:
        logging.critical(f"Pipeline crashed: {e}")