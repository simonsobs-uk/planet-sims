#!/usr/bin/env bash

# This is the no. of logical CPUs requested
REQUEST_CPUS="$(condor_q -jobads "$_CONDOR_JOB_AD" -af RequestCpus)"
echo "$REQUEST_CPUS logical CPUs requested" >&2
# devide this by 2 to get the no. of physical CPUs
REQUEST_CPUS="$((REQUEST_CPUS / 2))"
echo "$REQUEST_CPUS physical CPUs requested" >&2

export OPENBLAS_NUM_THREADS="$REQUEST_CPUS"
export JULIA_NUM_THREADS="$REQUEST_CPUS"
export TF_NUM_THREADS="$REQUEST_CPUS"
export MKL_NUM_THREADS="$REQUEST_CPUS"
export NUMEXPR_NUM_THREADS="$REQUEST_CPUS"
export OMP_NUM_THREADS="$REQUEST_CPUS"
echo "*_NUM_THREADS set to $REQUEST_CPUS" >&2

while true; do
    date >&2
    free -h >&2
    sleep 60
done &

echo '========================================================================' >&2
echo "HTCondor config summary:" >&2
echo '------------------------------------------------------------------------' >&2
condor_config_val -summary >&2

echo '========================================================================' >&2
echo "Current environment:" >&2
echo '------------------------------------------------------------------------' >&2
env >&2

echo '========================================================================' >&2
echo "CPU info:" >&2
echo '------------------------------------------------------------------------' >&2
# cat /proc/cpuinfo
lscpu >&2

echo '========================================================================' >&2
echo "Memory info:" >&2
echo '------------------------------------------------------------------------' >&2
cat /proc/meminfo >&2
# lsmem

echo '========================================================================' >&2
echo 'Unpacking environment...' >&2
tar -xzf pmpm-20230718-Linux-x86_64-OpenMPI.tar.gz -C /tmp >&2
. /tmp/pmpm-20230718/bin/activate /tmp/pmpm-20230718 >&2
echo '------------------------------------------------------------------------' >&2
echo 'Environment is available at:' >&2
which python >&2

echo '========================================================================' >&2
echo 'Running run_planet_sims_pipeline.py...' >&2
command time -v ./run_planet_sims_pipeline.py "$@"
