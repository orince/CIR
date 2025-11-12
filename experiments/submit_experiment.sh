#!/bin/bash
###
 # @Author: Naixin && naixinguo2-c@my.cityu.edu.hk
 # @Date: 2024-08-06 15:08:13
 # @LastEditors: Naixin && naixinguo2-c@my.cityu.edu.hk
 # @LastEditTime: 2024-08-19 22:12:44
 # @FilePath: /guonaixin/chr/experiments/submit_experiment.sh
 # @Description: 
 # 
### 

# Parameters
# N_LIST=(150 200 250 300 400 500 1000 2000 3000 4000 5000)
N_LIST=(300 400 500 1000 2000 3000 4000 5000)

# N_LIST=(500 2000 5000)
SYMMETRY_LIST=( 0 3 5 7 10 15 20 30 ) # 40 50
# SYMMETRY_LIST=(0)
ALPHA_LIST=(0.1)
BATCH_LIST=$(seq 1 100)
BATCH_SIZE=1
# Slurm parameters
MEMO=5G                             # Memory required (5GB)
TIME=02:00:00                       # Time required (2h)

# Assemble order prefix
ORDP="sbatch --mem="$MEMO" --nodes=1 --ntasks=1 --cpus-per-task=1 --time="$TIME

# Create directory for log files
LOGS="logs"
mkdir -p $LOGS

OUT_DIR="results_rf"
mkdir -p $OUT_DIR
mkdir -p "tmp_synthetic_rf"

# Function to process each combination of parameters
process_job() {
  ALPHA=$1
  BATCH=$2
  N=$3
  SYMMETRY=$4

  JOBN=$N"_"$SYMMETRY"_"$BATCH"_"$ALPHA

  OUT_FILE=$OUT_DIR"/synthetic_s"$SYMMETRY"_n"$N"_b"$BATCH"_a"$ALPHA".txta"

  if [[ ! -f $OUT_FILE ]]; then
    # Script to be run
    SCRIPT="experiment_synthetic.sh $N $SYMMETRY $ALPHA $BATCH $BATCH_SIZE"
    # Define job name for this combination
    OUTF=$LOGS"/"$JOBN".out"
    ERRF=$LOGS"/"$JOBN".err"
    # Assemble slurm order for this job
    ORD=$ORDP" -J "$JOBN" -o "$OUTF" -e "$ERRF" "$SCRIPT
    # Print order
    echo $SCRIPT
    # Submit order
    #$ORD
    # Run command now
    ./$SCRIPT
  fi
}

# Export the function to make it available to GNU Parallel
export -f process_job

# Generate all combinations of parameters
args=()
for ALPHA in "${ALPHA_LIST[@]}"; do
  for BATCH in $BATCH_LIST; do
    for N in "${N_LIST[@]}"; do
      for SYMMETRY in "${SYMMETRY_LIST[@]}"; do
        args+=("$N $SYMMETRY $ALPHA $BATCH $BATCH_SIZE ")
      done
    done
  done
done

# Run jobs in parallel
parallel -j 80 'taskset -c {%} bash -c "process_job {}"' ::: "${args[@]}"