#!/usr/bin/env python

import sys

from pixell import enplot
from sotodlib import coords, core

ctx = core.Context("context/context.yaml")
if len(sys.argv) <= 1:
    for obs in ctx.obsdb.get():
        print(obs["obs_id"])
    sys.exit(0)

for obs_id in sys.argv[1:]:
    this_obs = ctx.obsdb.get(obs_id)
    for wafer_slot in this_obs["wafer_slots"].split(","):
        print(obs_id, wafer_slot)

        tod = ctx.get_obs(obs_id, dets={"dets:wafer_slot": wafer_slot})
        center_on = tod.obs_info["target"]

        if tod.obs_info.telescope == "LAT":
            res, size = 0.005 * coords.DEG, 3 * coords.DEG
        else:
            # SAT!
            res, size = 0.02 * coords.DEG, 6 * coords.DEG

        with coords.Timer("compute_source_flags"):
            source_flags = coords.planets.compute_source_flags(
                tod=tod,
                center_on=center_on,
                max_pix=6e6,
                mask={"shape": "circle", "xyr": (0.0, 0.0, 0.1)},
            )

        with coords.Timer("make_map call"):
            maps = coords.planets.make_map(
                tod,
                # signal=signal_deconv,
                center_on=center_on,
                scan_coords=False,
                thread_algo="domdir",  # args.thread_algo,
                res=res,
                size=size,
                comps="T",  # args.comps,
                # filename=args.map_name,
                source_flags=source_flags,
                # cuts=glitch_flags,
                n_modes="all",
                low_pass=1.0,
                info={"obs_id": "test"},
            )  # args.obs_id})

        # with coords.Timer('Saving'):
        #    maps['solved'].write('map.fits')

        with coords.Timer("Plotting"):
            out_png = f"{obs_id}-{wafer_slot}-ctx.png"
            (p,) = enplot.plot(maps["solved"], grid=0, tile=-1)
            enplot.write(out_png, p)
