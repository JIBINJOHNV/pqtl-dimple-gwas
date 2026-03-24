# 📥 UKB-PPP Data Download from Synapse (Full CLI + HPC Guide)

This document provides a **step-by-step, reproducible workflow** to access and download **UK Biobank Pharma Proteomics Project (UKB-PPP)** data from Synapse using the command-line interface.

---

## 📌 Overview

* Platform: Synapse (Sage Bionetworks)
* Data type: UKB-PPP proteomics GWAS / summary statistics
* Access: Controlled (requires login + approval)
* Recommended usage: CLI for **HPC / pipeline integration**

---

## 🔗 Step 1: Access Synapse Project

* Main project:
  [https://www.synapse.org/Synapse:syn51364943](https://www.synapse.org/Synapse:syn51364943)

* Example dataset:
  [https://www.synapse.org/Synapse:syn51365301](https://www.synapse.org/Synapse:syn51365301)

---

## 🔐 Step 2: Create Synapse Account

1. Visit: [https://accounts.synapse.org/?appId=synapse.org](https://accounts.synapse.org/?appId=synapse.org)
2. Sign in / create account
3. Enable **Two-Factor Authentication (2FA)**

---

## 🔑 Step 3: Generate Personal Access Token

1. Go to **Profile → Account Settings**
2. Scroll to **Personal Access Tokens**
3. Click **Create New Token**
4. Assign appropriate permissions (default is fine)
5. Copy token securely

📖 Documentation:
[https://docs.synapse.org/synapse-docs/managing-your-account#ManagingYourAccount-PersonalAccessTokens](https://docs.synapse.org/synapse-docs/managing-your-account#ManagingYourAccount-PersonalAccessTokens)

---

## 🧰 Step 4: Install Synapse CLI

```bash
pip install synapseclient
```

Verify installation:

```bash
synapse --help
```

---

# ⚙️ Step 5: Authentication & Configuration (CRITICAL)

---

## 🔹 Step 5.1: Login (MANDATORY FIRST STEP)

```bash
synapse login -p $MY_SYNAPSE_TOKEN
```

* Uses your Personal Access Token
* Confirms access permissions
* Required before configuration

---

## 🔹 Step 5.2: Configure CLI (Persistent Setup)

```bash
synapse config
```

This stores credentials locally:

```bash
~/.synapseConfig
```

---

### Example Configuration File

```ini
[authentication]
username = your_username
authtoken = your_personal_access_token

[endpoint]
repoEndpoint = https://repo-prod.prod.sagebase.org/repo/v1
```

---

## 📂 Step 6: Identify Dataset (synID)

Each dataset/folder has a **Synapse ID (synID)**.

Example:

```bash
syn51365306
```

---

## 📥 Step 7: Download Data (Recursive)

---

### 🔹 Step 7.1: Create Output Directory

```bash
mkdir -p /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_East_Asian_syn51365306
```

---

### 🔹 Step 7.2: Download (HPC-Compatible)

```bash
nohup synapse get \
  --recursive \
  --downloadLocation /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_East_Asian_syn51365306 \
  syn51365306 \
  > download_UKB-PPP_East_Asian_syn51365306.log 2>&1 &
```

---

## 📊 Step 8: Monitor Download

```bash
tail -f download_UKB-PPP_East_Asian_syn51365306.log
```

---

## 🧠 Best Practices for Bioinformatics Pipelines

### ✅ Reproducibility

* Store:

  * synID
  * download path
  * timestamp
* Maintain a **manifest file (CSV/YAML)**


## 🚀 Optional: Python API Alternative

```python
import synapseclient

syn = synapseclient.Synapse()
syn.login(authToken="YOUR_TOKEN")

syn.get(
    "syn51365306",
    downloadLocation="/mnt/nethome/jjohn41/gwas_sumstat/raw_data/",
    recursive=True
)
```

---


## ✅ Final Minimal Workflow

```bash
# Login
synapse login -p $MY_SYNAPSE_TOKEN

# Configure
synapse config

# Download
nohup synapse get --recursive \
  --downloadLocation /mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_East_Asian_syn51365306 \
  syn51365306 \
  > download.log 2>&1 &
```

---

## 📚 References

* Synapse CLI Docs:
  [https://python-docs.synapse.org/en/stable/tutorials/command_line_client/](https://python-docs.synapse.org/en/stable/tutorials/command_line_client/)

* Token Management:
  [https://docs.synapse.org/synapse-docs/managing-your-account](https://docs.synapse.org/synapse-docs/managing-your-account)