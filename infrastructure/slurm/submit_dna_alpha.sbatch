#!/bin/bash
#SBATCH --job-name=gisap-dna-alpha
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --partition=bio-compute

echo "=== GISAP Nextflow Slurm HPC Execution ==="
echo "Node: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Start Time: $(date -u)"

# Load Apptainer / Nextflow environment modules
module load nextflow/23.10.0 || true
module load apptainer/1.2.0 || true

export NXF_OPTS="-Xms2g -Xmx8g"
export NXF_APPTAINER_CACHEDIR="$SCRATCH/apptainer_cache"

# Execute Nextflow DNA Alpha workflow with checkpointing and auto-resume
nextflow run workflows/nextflow/dna_alpha.nf \
    -profile slurm,apptainer \
    -c infrastructure/slurm/slurm_nextflow.config \
    --query_s3_uri "$1" \
    --reference_s3_uri "$2" \
    --output_dir "$3" \
    -resume

echo "Workflow completed at: $(date -u)"
