#!/usr/bin/env bash

while true; do
    date
    free -h
    sleep 60
done &

echo '========================================================================'
echo "HTCondor config summary:"
echo '------------------------------------------------------------------------'
condor_config_val -summary

echo '========================================================================'
echo "Current environment:"
echo '------------------------------------------------------------------------'
env

echo '========================================================================'
echo "CPU info:"
echo '------------------------------------------------------------------------'
# cat /proc/cpuinfo
lscpu

echo '========================================================================'
echo "Memory info:"
echo '------------------------------------------------------------------------'
cat /proc/meminfo
# lsmem

echo '========================================================================'
echo 'Unpacking environment...'
tar -xzf pmpm-20230718-Linux-x86_64-OpenMPI.tar.gz -C /tmp
. /tmp/pmpm-20230718/bin/activate /tmp/pmpm-20230718
echo '------------------------------------------------------------------------'
echo 'Environment is available at:'
which python

echo '========================================================================'
echo 'Running run_planet_sims_pipeline.py...'
command time -v ./run_planet_sims_pipeline.py c1 Jupiter
