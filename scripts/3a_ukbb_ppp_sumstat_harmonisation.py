import os 
import pandas as pd
import numpy as np
import subprocess


# --- Configuration ---
output_folder = '/mnt/fast/Analysis/ukb-ppp_harmonisation/harmonised_vcf_files/'
resource_folder = '/mnt/fast/Resourses/postgwas_resource/gwas2vcf/'
raw_data_folder = '/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/'
default_yaml = '/mnt/fast/Resourses/postgwas/tests/harmonisation.yaml'
image = "jibinjv/postgwas:1.3"



# Create directories if they don't exist
log_folder = os.path.join(output_folder, "logs")
os.makedirs(log_folder, exist_ok=True)

# Get current User and Group ID for Docker permissions
uid = os.getuid()
gid = os.getgid()



# --- Step 1: Create Master Map ---
print("🛠️  Step 1: Generating master sumstat map...")
cmd1 = f'''docker run --platform=linux/amd64 \
  -u {uid}:{gid} \
  -v /mnt/fast/:/mnt/fast/ \
  {image} python /opt/postgwas/src/postgwas/scripts/create_sumstat_map_pl.py \
  --input {raw_data_folder} \
  --output-path {output_folder}ukb-ppp_harmonisation_master_inputfile.csv \
  --resource-folder {resource_folder} \
  --harmonisation-output-path {output_folder}'''

# Run synchronously as this must finish before splitting
os.system(cmd1)

# --- Step 2: Split Data into 15 Chunks ---
master_csv = f"{output_folder}ukb-ppp_harmonisation_master_inputfile.csv"
if not os.path.exists(master_csv):
    raise FileNotFoundError(f"❌ Master file not found at {master_csv}. Check Step 1 logs.")

print(f"📄 Step 2: Splitting {master_csv} into 15 chunks...")
df = pd.read_csv(master_csv)
df_chunks = np.array_split(df, 10)

# Save chunks (1-based indexing)
for i, chunk in enumerate(df_chunks, 1):
    chunk_path = f"{output_folder}ukb-ppp_harmonisation_master_inputfile_chunk{i}.csv"
    chunk.to_csv(chunk_path, index=False)

# --- Step 3: Parallel Execution ---
print(f"🚀 Step 3: Initializing 15 simultaneous jobs (Available RAM: 995GB)...")

for i in range(1, 11):  # 1 through 15
    container_name = f"postgwas_batch_{i}"
    config_file = f"{output_folder}ukb-ppp_harmonisation_master_inputfile_chunk{i}.csv"
    log_file = f"{log_folder}/postgwas_batch_{i}.log"
    if not os.path.exists(config_file):
        print(f"⚠️  Warning: {config_file} not found. Skipping chunk {i}.")
        continue
    # Cleanup: Remove existing container with same name to avoid conflict
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    # Docker Command with log redirection
    # Note: Use -d so Docker runs in background, and '>' to catch logs in a file
    docker_cmd = f"""docker run --platform=linux/amd64 \
        -u {uid}:{gid} \
        -v /mnt/fast/:/mnt/fast/ \
        --name {container_name} \
        {image} \
        postgwas harmonisation \
        --nthreads 10 \
        --max-mem 50G \
        --config {config_file} \
        --defaults {default_yaml} > {log_file} 2>&1"""
    # Dispatch via shell=True to handle the '>' redirection
    subprocess.Popen(docker_cmd, shell=True)
    print(f"✅ Dispatched: {container_name} | Log: logs/postgwas_batch_{i}.log")

print("\n🔥 All 11 containers are now running in the background.")
print(f"Check progress with: tail -f {log_folder}/*.log")