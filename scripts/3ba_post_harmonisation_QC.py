import os
import subprocess
import polars as pl
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

# --- CONFIGURATION ---
search_root = Path("/mnt/fast/Analysis/ukb-ppp_harmonisation/harmonised_vcf_files/")
output_dir = Path('/mnt/fast/Analysis/ukb-ppp_harmonisation/postharmonisation_QC/')
output_file = output_dir / "ukb_ppp_variant_summary_postgwas_harmonisation_summary.csv"

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

def get_bcftools_counts(vcf_path):
    """
    Runs bcftools plugin counts and parses the output.
    """
    try:
        # Define the sample ID from the filename
        sample_id = vcf_path.name.replace("_merged.vcf.gz", "")
        
        # Run bcftools
        result = subprocess.run(
            ['bcftools', 'plugin', 'counts', str(vcf_path)],
            capture_output=True, text=True, check=True
        )
        
        # Initialize dictionary with metadata
        data = {
            "sample": sample_id,
            "file_name": vcf_path.name,
            "n_samples": 0, "n_snps": 0, "n_indels": 0, "n_mnps": 0, "n_others": 0, "n_sites": 0
        }

        # Map labels. Using 'in' check to be robust against minor bcftools version changes
        label_map = {
            "samples": "n_samples",
            "SNPs": "n_snps",
            "INDELs": "n_indels",
            "MNPs": "n_mnps",
            "others": "n_others",
            "sites": "n_sites"
        }

        for line in result.stdout.splitlines():
            if ":" in line:
                label, value = line.split(":", 1)
                for key_word, column in label_map.items():
                    if key_word in label:
                        data[column] = int(value.strip().replace(",", ""))
        return data

    except Exception as e:
        print(f"Error processing {vcf_path.name}: {e}")
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    file_patterns = [
        "*_GRCh37_notlifted_merged.vcf.gz",
        "*_GRCh38_merged.vcf.gz",
        "*_GRCh37_merged.vcf.gz"
    ]

    # 1. Collect all matching files
    all_vcf_files = []
    for pattern in file_patterns:
        all_vcf_files.extend(list(search_root.rglob(pattern)))

    # Remove duplicates if any (in case patterns overlap)
    all_vcf_files = list(set(all_vcf_files))
    
    print(f"Found {len(all_vcf_files)} total VCF files.")

    # 2. RUN IN PARALLEL (Use 12-20 workers)
    max_workers = 10 
    print(f"Starting parallel scan with {max_workers} workers...")

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Note: Using all_vcf_files[:10] here is recommended for a test run first!
        results = list(executor.map(get_bcftools_counts, all_vcf_files))

    # 3. Filter out None results (errors) and create DataFrame
    final_results = [r for r in results if r is not None]
    
    if final_results:
        df = pl.DataFrame(final_results)
        
        # Save results
        df.write_csv(output_file)
        print(f"\nScan Complete. Successfully processed {len(final_results)} files.")
        print(f"Summary saved to: {output_file}")
        print(df.head())
    else:
        print("No data was successfully extracted.")