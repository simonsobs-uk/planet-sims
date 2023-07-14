# Running

```sh
module load tod_stack_unstable
./run.lat.stage1.sh
mkdir -p schedules_reduced
head -n 4 schedules/schedule_c1_Jupiter.txt > schedules_reduced/schedule_c1_Jupiter.txt
./run.lat.stage2.sh
./write_context.py 'out_f*'
```
