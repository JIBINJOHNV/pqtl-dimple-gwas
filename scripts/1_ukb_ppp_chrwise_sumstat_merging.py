import os
import pandas as pd
import polars as pl
from pathlib import Path
import glob
import re
import subprocess
import shutil
from concurrent.futures import ProcessPoolExecutor


os.system(f"""ls /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303/*tar > \
        /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303/UKB-PPP_syn51365303_sumstat_path.txt """)

# --- Global Config ---
INPUT_LIST = '/mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303/UKB-PPP_syn51365303_sumstat_path.txt'
COMBINED_DIR = '/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/'
TEMP_DIR = '/mnt/fast/Analysis/ukb-ppp_harmonisation/'

def process_protein(file_path):
    """
    Function to process a single protein tarball with integrity checks.
    """
    protein_prefix = Path(file_path).name.replace(".tar", "")
    work_dir = Path(TEMP_DIR) / protein_prefix
    
    try:
        # 1. Setup paths
        work_dir.mkdir(parents=True, exist_ok=True)
        tar_dest = work_dir / Path(file_path).name
        
        # 2. Copy and Integrity Check Tar
        print(f"📦 [{protein_prefix}] Checking and Extracting...")
        shutil.copy(file_path, tar_dest)
        
        # Check if tar is valid before extracting
        if subprocess.run(["tar", "-tf", tar_dest], capture_output=True).returncode != 0:
            raise ValueError("Corrupted Tar archive")

        subprocess.run(["tar", "-xf", tar_dest, "-C", work_dir], check=True)

        # 3. File Discovery & Gzip Integrity Check
        files = glob.glob(str(work_dir / protein_prefix / "*.gz"))
        if not files:
            raise ValueError("No .gz files found after extraction")

        for f in files:
            # Check if each chromosome file is a valid gzip
            if subprocess.run(["gzip", "-t", f], capture_output=True).returncode != 0:
                raise ValueError(f"Corrupted gzip: {Path(f).name}")

        files.sort(key=lambda f: (match := re.search(r'chr([\dXYMT]+)', f)) and (23 if match.group(1) == 'X' else int(match.group(1)) if match.group(1).isdigit() else 999))

        # 4. Polars Processing
        print(f"🚀 [{protein_prefix}] Merging chromosomes...")
        dfs = [pl.read_csv(f, separator=" ") for f in files]
        df = pl.concat(dfs)

        # 5. Transformations
        df = df.with_columns([
            pl.col("ID").str.replace(":imp:v1", "").str.replace_all(":", "_"),
            pl.when(pl.col("CHROM") == 23)
              .then(pl.lit("X"))
              .otherwise(pl.col("CHROM").cast(pl.Utf8))
              .alias("CHROM")
        ]).drop(['TEST', 'CHISQ', 'EXTRA'])

        # 6. Write and Compress
        output_tsv = Path(COMBINED_DIR) / f"{protein_prefix}.tsv"
        df.write_csv(output_tsv, separator="\t")

        compressor = "pigz" if shutil.which("pigz") else "gzip"
        subprocess.run([compressor, "-f", str(output_tsv)], check=True)

        # 7. Cleanup
        shutil.rmtree(work_dir)
        print(f"✅ [{protein_prefix}] Finished successfully.")
        return f"SUCCESS|{file_path}"

    except Exception as e:
        print(f"❌ [{protein_prefix}] Failed: {str(e)}")
        # Cleanup temp files if they exist to prevent disk bloat
        if work_dir.exists():
            shutil.rmtree(work_dir)
        return f"FAILED|{file_path}|{str(e)}"

# --- Main Execution ---
if __name__ == "__main__":
    input_df = pd.read_csv(INPUT_LIST, sep="\t", header=None)
    file_list = input_df[0].tolist()
    Path(COMBINED_DIR).mkdir(parents=True, exist_ok=True)

    MAX_PARALLEL_PROTEINS = 10

    print(f"🔥 Starting parallel processing with {MAX_PARALLEL_PROTEINS} workers...")
    with ProcessPoolExecutor(max_workers=MAX_PARALLEL_PROTEINS) as executor:
        results = list(executor.map(process_protein, file_list))

    # --- Processing Results ---
    successful = [res.split("|")[1] for res in results if res.startswith("SUCCESS")]
    failures = [res.split("|")[1:] for res in results if res.startswith("FAILED")]

    # Write failed items to file
    if failures:
        fail_file = Path(COMBINED_DIR) / "failed_proteins.txt"
        with open(fail_file, "w") as f:
            for fail_info in failures:
                # fail_info[0] is the path, fail_info[1] is the error message
                f.write(f"{fail_info[0]}\t{fail_info[1]}\n")
        print(f"\n⚠️ {len(failures)} proteins failed. Details saved to: {fail_file}")

    print(f"\n--- Final Summary ---")
    print(f"✅ Successes: {len(successful)}")
    print(f"❌ Failures:  {len(failures)}")
