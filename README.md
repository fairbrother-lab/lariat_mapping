# Lariat Mapping | The Fairbrother Lab

## Overview

A pipeline for mapping lariat-derived reads present in RNA-seq data through the identification of reads with gapped, inverted alignments to introns.

## Dependencies

This pipeline has the following dependencies:
- python3 (tested with v3.10.6)
- bowtie2 (tested with v2.4.5)
- samtools (tested with v1.15.1)
- bedtools (tested with v2.30.0)
- numpy (tested with v1.23.2)
- [pyfaidx](https://pypi.org/project/pyfaidx/) (tested with v0.7.2.1)
- [intervaltree](https://pypi.org/project/intervaltree/) (tested with v3.1.0)

These dependencies are included in the file `environment.yaml` which can be used to make a conda environment for the pipeline by running `conda env create -f environment.yaml`. Then, activate the environment with `conda activate larmap_env` 

For M1 mac users: please install packages `bowtie2`, `bedtools`, and `samtools` using the command `arch -arm64 brew install [package]` before running `conda`, if any of the above pacakges has not previously been installed.

## Reference Files

The pipeline requires the following standard reference files: FASTA file of the reference genome, bowtie2 index of the reference genome, GTF file containing gene annotation of the reference genome, and BED file containing introns of the reference genome. For each reference genome, please also run `python get_splice_site_seqs.py [introns.bed] [genome.fa] [output_name_prefix]` to produce the custom reference files required for the pipeline. After running this script, use `bowtie2-build` on the resulting `[output_name_prefix].threep_sites.fa` file. In addition, the pipeline requires a BED file containing the RepeatMasker annotation for the mapping genome. For hg19 and hg38, this file can be obtained from the [UCSC table browser](https://genome.ucsc.edu/cgi-bin/hgTables).

## Running the Pipeline

`larmap_setup.py` takes two tab-separated info files and generates the scripts for performing the lariat mapping runs. The run info file is formatted as follows:
      
      scripts_dir           Path to lariat mapping directory
      fastq_dir             Path to directory containing the FASTQ files to process
      output_dir            Path to output directory
      num_cpus              Number of CPUs to use
      ref_fasta             Path to reference genome FASTA file
      ref_b2index           Path to reference genome bowtie2 index
      ref_gtf               Path to reference genome GTF annotation file
      ref_introns           Path to reference genome intron BED file
      ref_5p_fasta          Path to 5'ss FASTA file generated by `get_splice_site_seqs.py`
      ref_5p_upstream       Path to 5'ss upstream sequence file generated by `get_splice_site_seqs.py`
      ref_3p_b2index        Path to bowtie2 index of 3'ss FASTA file generated by `get_splice_site_seqs.py`
      ref_3p_lengths        Path to 3'ss sequence lengths file generated by `get_splice_site_seqs.py`
      ref_repeatmasker      Path to RepeatMasker BED annotation file

The sample info file contains an arbitrary number of columns describing, eg., cell line, experimental treatment, replicate number, etc. followed by a final column that contains the name of the sample's read file. This read file should be present in the directory `fastq_dir` given in the run info file. The sample info file is expected to have a single line header of column names. An example is given below:

      cell_line    replicate      read_file
      HEK293T      1              HEK293T_1.fq.gz
      HEK293T      2              HEK293T_2.fq.gz
      HEK293T      3              HEK293T_3.fq.gz

`larmap_setup.py` will create one bash script for each line in the sample info file. The output for a given read file will be written to `output_dir` from the run info file under a directory named from a concatenation of all but the last column in the sample info file followed by `_lariat_mapping` (eg. `HEK293T_1_lariat_mapping`). After running `larmap_setup.py [run_info.txt] [sample_info.txt]`, you can run each generated bash script to perform the lariat mapping for that read file.

Alternatively, to run the pipeline on a single file, use `larmap_run.sh` with the following arguments:

      -r, --read_file           FASTQ file
      -o, --output_dir          Directory for output files
      -e, --output_base_name    Prefix to add to output files
      -c, --num_cpus            Number of CPUs available
      -i, --ref_b2index         Bowtie2 index of the full reference genome
      -f, --ref_fasta           FASTA file of the full reference genome
      -g, --ref_gtf             GTF file with gene annotation of the reference genome
      -5, --ref_5p_fasta        FASTA file with sequences of first 20nt from reference 5' splice sites (first 20nt of introns)
      -u, --ref_5p_upstream     Custom file of sequences in 5nt window upstream of 5' splice sites
      -3, --ref_3p_b2index      Bowtie2 index file of last 250nt from reference 3' splice sites (last 250nt of introns)
      -l, --ref_3p_lengths      Custom file with the lengths of the sequences in ref_3p_b2index (some introns are <250nt)
      -n, --ref_introns         BED file of all introns in the reference genome
      -m, --ref_repeatmasker    BED file of repetitive elements from RepeatMasker

A directory named `[output_base_name]_lariat_mapping` will be created in `output_dir`. Upon completion of the pipeline, this directory will contain a tab-separated results file with lariat read info called `[output_base_name]_lariat_reads.txt`.

## Pipeline Workflow

1. `larmap_run.sh` calls `map_lariats.sh` on the FASTQ file. This will produce three files in the output subdirectory for the read file:
    -`[output_base_name]_total_reads.txt` (one line file containing count of linearly-aligned reads from the read file)
    - `[output_base_name]_fivep_info_table.txt` (intermediate file containing info on the mapping of the 5'SS sequences to the unmapped reads)
    - `[output_base_name]_final_info_table.txt` (results file containing candidate lariat reads obtained after mapping the 5'SS trimmed reads to the 3'SS region sequences)

    The mapping script `map_lariats.sh` will:
    - Align reads to the reference genome with bowtie2; save mapped read count and proceed with unmapped reads
    - Convert the unmapped reads bam file to FASTA format with samtools
    - Build a bowtie2 index of the unmapped reads FASTA file
    - Align a FASTA file of 5'SS to the unmapped reads index
    - Trim reads with 5'SS alignments and write trimmed reads to FASTA file
    - Align the trimmed reads to a Bowtie2 index of 3'SS regions
    - Take the mapped trimmed reads from and create an output file containing candidate lariat reads

3. The `filter_lariats.py` script loads intron and gene information from provided annotation files and performs post-mapping filtering before outputting the final lariat mapping results. 

    The candidate lariat reads are filtered based on the following criteria:
         - BP is within 2bp of a splice site (likely from an intron circle, not a lariat)
         - 5'SS and 3'SS are not in the correct order - Read maps to a Ubiquitin gene (likely false positive due to repetitive nature of gene)
         - There is a valid aligment for the 3' segment upstream of the 5' segment
         - Both the 5'SS and the BP overlap with repetitive regions from RepeatMasker (likely false positive)
