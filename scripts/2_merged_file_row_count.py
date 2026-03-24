import glob
import subprocess
import os

# Configuration
folder_path = "/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/"
# Changed extension to .csv
output_file = os.path.join(folder_path, "ukb-ppp_EUR_AllChr_merged_row_counts.csv")
corrupt_log = os.path.join(folder_path, "ukb-ppp_EUR_AllChr_merged_corrupted_files.txt")

# Find all .gz files
gz_files = glob.glob(os.path.join(folder_path, "*.gz"))
corrupted_list = []

print(f"Checking integrity and counting variants for {len(gz_files)} files...", flush=True)

with open(output_file, "w") as out:
    # Header using commas for CSV format
    out.write("filename,variant_count,status\n")
    
    for f in gz_files:
        filename = os.path.basename(f)
        
        # 1. Integrity Check (gzip -t)
        check = subprocess.run(["gzip", "-t", f], capture_output=True)
        
        if check.returncode != 0:
            status = "CORRUPTED"
            variant_count = "N/A"
            corrupted_list.append(filename)
            print(f"❌ {filename}: {status}", flush=True)
        else:
            # 2. Faster Row Count using the pipe method
            cmd = f"zcat < '{f}' | wc -l"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            try:
                total_rows = int(result.stdout.strip())
                # Variant count is Total Rows minus the header line
                variant_count = total_rows - 1 if total_rows > 0 else 0
                status = "VALID"
                print(f"✅ {filename}: {variant_count} variants", flush=True)
            except ValueError:
                status = "ERROR_READING"
                variant_count = "N/A"
                print(f"⚠️ {filename}: Could not parse row count", flush=True)
        
        # Write to results using commas and force sync to disk
        out.write(f"{filename},{variant_count},{status}\n")
        out.flush() 

# Final Summary logic
if corrupted_list:
    with open(corrupt_log, "w") as f_err:
        for item in corrupted_list:
            f_err.write(f"{item}\n")
    print(f"\n⚠️ Warning: {len(corrupted_list)} corrupted files found. Check: {corrupt_log}", flush=True)
else:
    print("\n🎉 All files passed integrity check.", flush=True)

print(f"Finished! Results saved to: {output_file}", flush=True)