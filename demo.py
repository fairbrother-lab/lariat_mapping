from larmap import (larmap, map_lariats)

sample_args_str = 'demo_files/demo_fastq_files_250k_bp 250k_cWT_1.fq.gz 250k_cWT_2.fq.gz 250k_cDBR1-Y17H_1.fq.gz 250k_cDBR1-Y17H_2.fq.gz WT Y17H 4 demo_files/genomes/indices/bowtie2/mm39.fa demo_files/genomes/fasta_files/mm39.fa demo_files/genomes/annotations/mm39.gencode.basic.M32.annotation.gtf.gz demo_files/reference_files/mouse/mm39.gencode.basic.M32.fivep_sites.fa demo_files/reference_files/mouse/mm39.gencode.basic.M32.threep_sites.fa demo_files/reference_files/mouse/mm39.gencode.basic.M32.threep_seq_lens.txt demo_files/genomes/annotations/mm39.gencode.basic.M32.introns.bed.gz demo_files/genomes/annotations/mm39.repeat_masker.bed.gz demo_mapped_reads_250k.txt'
args = sample_args_str.split(' ')

larmap_runObj = larmap(*args)
map_lariats(larmap_runObj)