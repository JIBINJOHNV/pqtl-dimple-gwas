
# PURPOSE:
# Confirm total variant counts in the concatenated (all chromosomes) summary statistics files.
# These merged files serve as the input for the subsequent PostGWAS harmonisation pipeline.



base_dir='/mnt/nethome/jjohn41/gwas_sumstat/raw_data/UKB-PPP/UKB-PPP_European_syn51365303/'
mkdir ${base_dir}/test/


## copy the the files to test directory
cp ${base_dir}/NPM1_P06748_OID20961_v1_Neurology.tar ${base_dir}/test/
cp ${base_dir}/PCOLCE_Q15113_OID20384_v1_Cardiometabolic.tar ${base_dir}/test/
cp ${base_dir}/CTSS_P25774_OID21056_v1_Neurology.tar ${base_dir}/test/
cp ${base_dir}/CST1_P01037_OID30581_v1_Inflammation_II.tar ${base_dir}/test/



for dir in NPM1_P06748_OID20961_v1_Neurology PCOLCE_Q15113_OID20384_v1_Cardiometabolic CTSS_P25774_OID21056_v1_Neurology CST1_P01037_OID30581_v1_Inflammation_II; do
    total=$(zcat "${base_dir}/test/${dir}"/*.gz | wc -l)
    adjusted=$((total - 23))
    echo "${dir}: ${adjusted}" >> ${base_dir}/test/protein_counts.txt
done