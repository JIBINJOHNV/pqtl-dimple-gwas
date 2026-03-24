import os
import polars as pl
from pathlib import Path
import logging
from datetime import datetime

# --- CONFIGURATION ---
INPUT_DIR = Path("/mnt/fast/Analysis/ukb-ppp_harmonisation/ukb-ppp_zscore_matrix/")
TEMP_DIR = Path("/mnt/fast/Analysis/ukb-ppp_harmonisation/temp_batches/")
FINAL_OUTPUT = Path("/mnt/fast/Analysis/ukb-ppp_harmonisation/ukb-ppp_zscore_matrix/ukb_ppp_zscore_full_matrix.tsv")
BATCH_SIZE = 200

# Setup
TEMP_DIR.mkdir(parents=True, exist_ok=True)
log_path = f"merge_z_score_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()]
)

def merge_batch(file_list, batch_index):
    """Joins a batch of files and returns the resulting DataFrame."""
    logging.info(f"--- Processing Batch {batch_index}: {len(file_list)} files ---")
    
    # Start with the first file
    batch_df = pl.read_csv(file_list[0], separator="\t")
    
    for i, file_path in enumerate(file_list[1:], 1):
        next_df = pl.read_csv(file_path, separator="\t")
        
        # Outer join on genomic keys
        batch_df = batch_df.join(
            next_df, 
            on=["CHROM", "POS", "ID", "REF", "ALT"], 
            how="outer"
        )
        
        if i % 50 == 0:
            logging.info(f"   [Batch {batch_index}] Merged {i}/{len(file_list)} files...")

    # Validation: Count columns (should be 5 keys + number of files)
    expected_cols = 5 + len(file_list)
    actual_cols = len(batch_df.columns)
    
    if expected_cols != actual_cols:
        logging.warning(f"   [Batch {batch_index}] Column mismatch! Expected {expected_cols}, got {actual_cols}")
    else:
        logging.info(f"   [Batch {batch_index}] Validation Passed: {actual_cols} columns generated.")

    batch_out = TEMP_DIR / f"batch_{batch_index}.parquet"
    batch_df.write_parquet(batch_out)
    return batch_out

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Initial Scan
    all_tsvs = sorted(list(INPUT_DIR.glob("*_zscore.tsv")))
    total_files = len(all_tsvs)
    
    if total_files == 0:
        logging.error("No input files found in Z_MATRIX_DIR. Exiting.")
        exit(1)

    logging.info(f"VALIDATION START: Found {total_files} total Z-score matrix files.")

    # 2. Iterative Batching
    batch_paths = []
    for i in range(0, total_files, BATCH_SIZE):
        batch_idx = (i // BATCH_SIZE) + 1
        current_slice = all_tsvs[i : i + BATCH_SIZE]
        
        batch_pqt = merge_batch(current_slice, batch_idx)
        batch_paths.append(batch_pqt)

    # 3. Final Integration
    logging.info("--- FINAL INTEGRATION: Merging all batch Parquet files ---")
    final_df = pl.read_parquet(batch_paths[0])

    for batch_pqt in batch_paths[1:]:
        logging.info(f"   Joining {batch_pqt.name} to master matrix...")
        next_batch = pl.read_parquet(batch_pqt)
        final_df = final_df.join(
            next_batch, 
            on=["CHROM", "POS", "ID", "REF", "ALT"], 
            how="outer"
        )

    # 4. FINAL VALIDATION REPORT
    final_cols = len(final_df.columns)
    final_rows = len(final_df)
    expected_final_cols = 5 + total_files # 5 keys + 2,940 (or however many files were found)

    logging.info("="*40)
    logging.info("FINAL QUALITY CONTROL REPORT")
    logging.info(f"Total Input Files: {total_files}")
    logging.info(f"Total Rows (SNPs): {final_rows}")
    logging.info(f"Total Columns:     {final_cols}")
    
    if final_cols == expected_final_cols:
        logging.info("SUCCESS: Final column count matches total input files.")
    else:
        logging.error(f"CRITICAL: Column mismatch! Expected {expected_final_cols}, found {final_cols}.")
    logging.info("="*40)

    # 5. Save Output
    logging.info(f"Writing compressed final matrix to: {FINAL_OUTPUT}")
    final_df.write_csv(FINAL_OUTPUT, separator="\t")
    logging.info("Pipeline complete.")