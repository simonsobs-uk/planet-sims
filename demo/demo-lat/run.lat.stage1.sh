#!/bin/bash

export OMP_NUM_THREADS=4  #never run with this unset on simons1!

tele="LAT"
tube=c1

echo Tube $tube
# NOTE:  for wafer offsets, use the --wafer_slot option
offsets=(`get_wafer_offset.py --tube_slots $tube`)
echo Offsets are ${offsets[@]}
offset_az=${offsets[0]}
offset_el=${offsets[1]}
tube_radius=${offsets[2]}

sso_name=Jupiter
echo "   $sso_name"

schedule=schedules/schedule_${tube}_${sso_name}.txt
toast_ground_schedule \
    --site-lat \
    -22.958064 \
    --site-lon \
    -67.786222 \
    --site-alt \
    5200 \
    --site-name \
    ATACAMA \
    --telescope ${tele} \
    --start "2023-06-08 00:00:00" \
    --stop "2023-06-09 00:00:00" \
    --patch ${sso_name},SSO,1,${tube_radius} \
    --boresight-offset-az-deg ${offset_az} \
    --boresight-offset-el-deg ${offset_el} \
    --out ${schedule} 

