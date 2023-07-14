#!/bin/bash

export OMP_NUM_THREADS=4  #never run with this unset on simons1!
#export OMP_NUM_THREADS=1
ntask=1

tele="LAT"
#tube=i1
#band=150
band_name=f`printf "%03i" $band`
#beam_dir=/mnt/so1/users/zhileixu/beam_model

function run_one() {
    #beam_file=${beam_dir}/${tele}_${band_name}_beam.p
    beam_file=/mnt/so1/shared/site-pipeline/bcp/${tele}_${band_name}_beam.h5
    prefix=${band_name}_${tube}_${sso_name}

    # NOTE:  These parameters can also be set with a config file...
    # The "names" of each operator in the command line arguments are just
    # the names given in the script being called (toast_so_sim.py in this
    # case).

    # export TOAST_LOGLEVEL=VERBOSE

    outdir="out_${prefix}"
    mkdir -p "${outdir}"

    mpirun -np ${ntask} toast_so_sim.py \
           `#--corotate_lat.no_corotate_lat` \
           `# Do not make a map, just write the timestreams` \
           --mapmaker.disable \
           `# Instrument params` \
           --tube_slots ${tube} \
           --bands LAT_${band_name} \
           --sample_rate "${fsample}" \
           `# Observing schedule` \
           --schedule ${schedule} \
           `# Scanning params` \
           --sim_ground.turnaround_mask 2 \
           --sim_ground.scan_rate_az '1.5 deg / s' \
           --sim_ground.scan_accel_az '3.0 deg / s2' \
           `# Use fixed weather parameters` \
           --sim_ground.median_weather \
           `# Simulated sky signal from a map` \
           --scan_map.disable \
           `# Simulated SSO` \
           --sim_sso.enable \
           --sim_sso.sso_name ${sso_name} \
           --sim_sso.beam_file ${beam_file} \
           `# Simulated atmosphere params (high resolution)` \
           --sim_atmosphere.enable \
           --sim_atmosphere.field_of_view '6 deg' \
           `# Simulated atmosphere params (coarse resolution)` \
           --sim_atmosphere_coarse.enable \
           --sim_atmosphere_coarse.field_of_view '6 deg' \
           `# Noise simulation (from elevation-modulated focalplane parameters)` \
           --sim_noise.enable \
           `# Gain mismatch` \
           `#--gainscrambler.enable` \
           `#--gainscrambler.sigma 0.01` \
           `# Timeconstant convolution` \
           --convolve_time_constant.enable \
           --convolve_time_constant.tau '3 ms' \
           `# Write to HDF5` \
           --save_hdf5.enable \
           --out_dir ${outdir} \
           --job_group_size ${ntask} | tee "${outdir}/log"
}


for tube in c1 i1 i5 i4; do 
    echo Tube $tube

    for sso_name in Uranus Saturn Mars Jupiter ; do
        echo "   $sso_name"

        case $tube in
            c1|i5)
                bands=( f230 f290 )
                fsample=200
                ;;
            i1|i3|i4|i6)
                bands=( f090 f150 )
                fsample=200
                ;;
            o6)
                bands=( f030 f040 )
                fsample=60
                ;;
        esac

        schedule=schedules_reduced/schedule_${tube}_${sso_name}.txt
        [ -e $schedule ] || continue

        for band_name in ${bands[@]}; do
            echo "    band=$band_name"
            run_one
        done

    done

done

