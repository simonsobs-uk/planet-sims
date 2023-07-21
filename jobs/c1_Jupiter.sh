#!/usr/bin/env bash

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
