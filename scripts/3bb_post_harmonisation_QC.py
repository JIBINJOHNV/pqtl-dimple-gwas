
import pandas as pd 
import subprocess
import numpy as np 

sample_name='ITGB2_P05107_OID20315_v1_Cardiometabolic'



merged_tsv_dir='/mnt/fast/Analysis/ukb-ppp_harmonisation/chr_mered_data/'
vcf_base_dir='/mnt/fast/Analysis/ukb-ppp_harmonisation/harmonised_vcf_files/'
out_dir='/mnt/fast/Analysis/ukb-ppp_harmonisation/postharmonisation_QC/Detailed_qc/'


# Using your f-string to define the command
cmd = f'''( echo -e "CHROM\\tPOS\\tID\\tREF\\tALT\\tES\\tSE\\tEZ\\tLP\\tAF\\tSI\\tSS\\tNCO\\tNEF"; \
bcftools query -f '%CHROM\\t%POS\\t%ID\\t%REF\\t%ALT\\t[%ES]\\t[%SE]\\t[%EZ]\\t[%LP]\\t[%AF]\\t[%SI]\\t[%SS]\\t[%NCO]\\t[%NEF]\\n' \
{vcf_base_dir}/{sample_name}/00_harmonised_sumstat/{sample_name}_GRCh38_merged.vcf.gz ) > \
{out_dir}/{sample_name}_vcf.tsv'''

try:
    # run the command
    subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
    print("Extraction successful: extracted_fields.tsv created.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")
 



df=pd.read_csv(f'{merged_tsv_dir}/{sample_name}.tsv.gz', sep='\t')
df.drop('ID',axis=1,inplace=True)

vcf_df=pd.read_csv(f'{out_dir}/{sample_name}_vcf.tsv', sep='\t')
vcf_df.drop('ID',axis=1,inplace=True)



merged_df1=pd.merge(df,vcf_df,left_on=['CHROM','GENPOS','ALLELE0','ALLELE1'],right_on=['CHROM','POS','REF','ALT'])
merged_df1['VARIANT_TYPE'] = np.where(
        (merged_df1['ALLELE0'].str.len() > 1) | (merged_df1['ALLELE1'].str.len() > 1), 
    'INDEL', 'SNP' )



es_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','BETA','REF', 'ALT', 'ES']] 
es_df['es_diff']= (es_df['BETA'] - es_df['ES']).abs()

es_df[es_df['es_diff']!=0.0]['VARIANT_TYPE'].unique()

es_df[(es_df['es_diff']!=0.0) & (es_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']

es_df[(es_df['es_diff']!=0.0) & (es_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']



af_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','A1FREQ','REF', 'ALT', 'AF']] 
af_df['af_diff']= (af_df['A1FREQ'] - af_df['AF']).abs()
af_df[af_df['af_diff']!=0.0]['VARIANT_TYPE'].unique()
af_df[(af_df['af_diff']!=0.0) & (af_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
af_df[(af_df['af_diff']!=0.0) & (af_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']



si_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','INFO','REF', 'ALT', 'SI']] 
si_df['si_diff']= (si_df['INFO'] - si_df['SI']).abs()
si_df[si_df['si_diff']!=0.0]['VARIANT_TYPE'].unique()
si_df[(si_df['si_diff']!=0.0) & (si_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
si_df[(si_df['si_diff']!=0.0) & (si_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']


lp_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','LOG10P','REF', 'ALT', 'LP']] 
lp_df['lp_diff']= (lp_df['LOG10P'] - lp_df['LP']).abs()
lp_df[lp_df['lp_diff']!=0.0]['VARIANT_TYPE'].unique()
lp_df[(lp_df['lp_diff']!=0.0) & (lp_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
lp_df[(lp_df['lp_diff']!=0.0) & (lp_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']



se_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','SE_x','REF', 'ALT', 'SE_y']] 
se_df['se_diff']= (se_df['SE_x'] - se_df['SE_y']).abs()
se_df[se_df['se_diff']!=0.0]['VARIANT_TYPE'].unique()
se_df[(se_df['se_diff']!=0.0) & (se_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
se_df[(se_df['se_diff']!=0.0) & (se_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']


ss_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','N','REF', 'ALT', 'SS', 'NCO', 'NEF']] 
ss_df['ss_diff']= (ss_df['N'] - ss_df['SS']).abs()
ss_df[ss_df['ss_diff']!=0.0]['VARIANT_TYPE'].unique()
ss_df[(ss_df['ss_diff']!=0.0) & (ss_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
ss_df[(ss_df['ss_diff']!=0.0) & (ss_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']

# Check if all columns are equal to 'SS'
mask = (ss_df['SS'] == ss_df['N']) & \
       (ss_df['SS'] == ss_df['NCO']) & \
       (ss_df['SS'] == ss_df['NEF'])

# Filter the dataframe
matching_rows = ss_df[mask]

# To see how many match vs how many don't:
print(f"Total rows: {len(ss_df)}")
print(f"Perfect matches: {mask.sum()}")
print(f"Mismatches: {(~mask).sum()}")




ez_df=merged_df1[['CHROM', 'GENPOS','VARIANT_TYPE' ,'ALLELE0', 'ALLELE1','BETA','SE_x','REF', 'ALT', 'ES', 'SE_y', 'EZ']] 
ez_df['EZ2']= (ez_df['BETA']/ez_df['SE_x'])

ez_df['ez_diff']= (ez_df['EZ'] - ez_df['EZ2']).abs()

ez_df[ez_df['ez_diff']!=0.0]['VARIANT_TYPE'].unique()
ez_df[(ez_df['ez_diff']!=0.0) & (ez_df['VARIANT_TYPE']=='SNP')]['VARIANT_TYPE']
ez_df[(ez_df['ez_diff']!=0.0) & (ez_df['VARIANT_TYPE']=='INDEL')]['VARIANT_TYPE']






merged_df2=pd.merge(df,vcf_df,left_on=['CHROM','GENPOS','ALLELE0','ALLELE1'],right_on=['CHROM','POS','ALT','REF'])

merged_df1['af_diff'] = (merged_df1['A1FREQ'] - merged_df1['AF']).abs()


af_dif=merged_df1[['CHROM', 'GENPOS', 'ALLELE0', 'ALLELE1','A1FREQ','REF', 'ALT', 'AF','af_diff']] 
af_dif[af_dif['af_diff']>0.001]


es_df=merged_df1[['CHROM', 'GENPOS', 'ALLELE0', 'ALLELE1','BETA','REF', 'ALT', 'ES']] 
es_df['es_diff']= (es_df['BETA'] - es_df['ES']).abs()