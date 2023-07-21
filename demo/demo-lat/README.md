# Running

```sh
module load tod_stack_unstable
./run.lat.stage1.sh
mkdir -p schedules_reduced
head -n 4 schedules/schedule_c1_Jupiter.txt > schedules_reduced/schedule_c1_Jupiter.txt
./run.lat.stage2.sh
./write_context.py 'out_f*'
# You get some very crude maps of an obs by running
map_context.py [obs_id]
```

I would like a set of ~6 sims each for tubes c1, i1, and i4; covering planets Uranus, Saturn, and Jupiter.
