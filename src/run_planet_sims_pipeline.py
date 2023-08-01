#!/usr/bin/env python

from __future__ import annotations

import io
import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import defopt
from astropy.utils.data import download_file
from sotodlib.workflows import get_wafer_offset, toast_so_sim
from toast.scripts import toast_ground_schedule

if TYPE_CHECKING:
    from typing import Callable

try:
    from coloredlogs import ColoredFormatter as Formatter
except ImportError:
    from logging import Formatter

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)
handler.setFormatter(Formatter("%(name)s %(levelname)s %(message)s"))
logger.setLevel(level=logging.WARNING)

# helpers to run any python function intended for cli ###########################################


@contextmanager
def tee_stdout(buffer):
    """Similar to redirect_stdout, but also prints to the original stdout."""
    cur_stdout = sys.stdout

    class TeeStdout:
        def __init__(self, buffer):
            self.buffer = buffer

        def write(self, data):
            self.buffer.write(data)
            cur_stdout.write(data)

        def flush(self):
            self.buffer.flush()
            cur_stdout.flush()

    sys.stdout = TeeStdout(buffer)
    try:
        yield
    finally:
        sys.stdout = cur_stdout


@contextmanager
def tee_stderr(buffer):
    """Similar to redirect_stderr, but also prints to the original stderr."""
    cur_stderr = sys.stderr

    class TeeStderr:
        def __init__(self, buffer):
            self.buffer = buffer

        def write(self, data):
            self.buffer.write(data)
            cur_stderr.write(data)

        def flush(self):
            self.buffer.flush()
            cur_stderr.flush()

    sys.stderr = TeeStderr(buffer)
    try:
        yield
    finally:
        sys.stderr = cur_stderr


def run_cli(
    func: Callable[[], None],
    args: list[str],
    capture_stdout: bool = True,
    capture_stderr: bool = True,
) -> tuple[str, str]:
    """Run any function that is intended to be run from the command line.

    For example, if you have an entry point `module.sub:main` that you can run
    with `python -m module.sub arg1 arg2 ...`, you can run it with this function like so:

    >>> stdout, stderr = run_cli(module.sub.main, ['arg1', 'arg2', ...])
    """
    stdout = ""
    stderr = ""
    if capture_stdout:
        if capture_stderr:
            f_out = io.StringIO()
            f_err = io.StringIO()
            with tee_stdout(f_out), tee_stderr(f_err):
                # https://stackoverflow.com/a/27765993/5769446
                with patch.object(sys, "argv", [func.__name__] + args):
                    func()
            stdout = f_out.getvalue()
            stderr = f_err.getvalue()
        else:
            f_out = io.StringIO()
            with tee_stdout(f_out):
                with patch.object(sys, "argv", [func.__name__] + args):
                    func()
            stdout = f_out.getvalue()
    elif capture_stderr:
        f_err = io.StringIO()
        with tee_stderr(f_err):
            with patch.object(sys, "argv", [func.__name__] + args):
                func()
        stderr = f_err.getvalue()
    else:
        with patch.object(sys, "argv", [func.__name__] + args):
            func()
    return stdout, stderr


# helpers to run the pipeline ###################################################################


def get_wafer_offset_func(
    tube: str,
) -> tuple[float, float, float]:
    stdout, _ = run_cli(
        get_wafer_offset.main, ["--tube_slots", tube], capture_stderr=False
    )
    offset_az, offset_el, tube_radius, _, _, _ = stdout.split()
    return float(offset_az), float(offset_el), float(tube_radius)


def toast_ground_schedule_func(
    path: Path,
    offset_az: float,
    offset_el: float,
    tube_radius: float,
    tele: str = "LAT",
    start: str = "2023-06-08 00:00:00",
    stop: str = "2023-06-09 00:00:00",
    sso_name: str = "Jupiter",
):
    _, _ = run_cli(
        toast_ground_schedule.main,
        [
            "--site-lat",
            "-22.958064",
            "--site-lon",
            "-67.786222",
            "--site-alt",
            "5200",
            "--site-name",
            "ATACAMA",
            "--telescope",
            tele,
            "--start",
            start,
            "--stop",
            stop,
            "--boresight-offset-az-deg",
            str(offset_az),
            "--boresight-offset-el-deg",
            str(offset_el),
            "--patch",
            f"{sso_name},SSO,1,{tube_radius}",
            "--out",
            str(path),
        ],
        capture_stdout=False,
        capture_stderr=False,
    )


def get_beam_file(tele: str, band_name: str) -> Path:
    """Download beam file."""
    return download_file(
        f"https://github.com/simonsobs-uk/planet-sims/releases/latest/download/{tele}_{band_name}_beam.h5",
        cache=True,
    )


def run_one(
    tele: str,
    band_name: str,
    tube: str,
    sso_name: str,
    fsample: float,
    schedule: Path,
    beam_file: Path,
    ntask: int = 1,
) -> None:
    prefix = f"{band_name}_{tube}_{sso_name}"
    outdir = Path(f"out_{prefix}")
    outdir.mkdir(exist_ok=True)

    stdout, stderr = run_cli(
        toast_so_sim.main,
        [
            "--mapmaker.disable",
            # Instrument params
            "--tube_slots",
            tube,
            "--bands",
            f"{tele}_{band_name}",
            "--sample_rate",
            str(fsample),
            # Observing schedule
            "--schedule",
            str(schedule),
            # Scanning params
            "--sim_ground.turnaround_mask",
            "2",
            "--sim_ground.scan_rate_az",
            "1.5 deg / s",
            "--sim_ground.scan_accel_az",
            "3.0 deg / s2",
            # Use fixed weather parameters
            "--sim_ground.median_weather",
            # Simulated sky signal from a map
            "--scan_map.disable",
            # Simulated SSO
            "--sim_sso.enable",
            "--sim_sso.sso_name",
            sso_name,
            "--sim_sso.beam_file",
            str(beam_file),
            # Simulated atmosphere params (high resolution)
            "--sim_atmosphere.enable",
            "--sim_atmosphere.field_of_view",
            "6 deg",
            # Simulated atmosphere params (coarse resolution)
            "--sim_atmosphere_coarse.enable",
            "--sim_atmosphere_coarse.field_of_view",
            "6 deg",
            # Noise simulation (from elevation-modulated focalplane parameters)
            "--sim_noise.enable",
            # Gain mismatch
            # "--gainscrambler.enable",
            # "--gainscrambler.sigma",
            # "0.01",
            # Timeconstant convolution
            "--convolve_time_constant.enable",
            "--convolve_time_constant.tau",
            "3 ms",
            # Write to HDF5
            "--save_hdf5.enable",
            "--out_dir",
            str(outdir),
            "--job_group_size",
            str(ntask),
        ],
        capture_stdout=True,
        capture_stderr=True,
    )
    with (outdir / "log.out").open("w") as f:
        f.write(stdout)
    with (outdir / "log.err").open("w") as f:
        f.write(stderr)


def stage1(
    tube: str,
    sso_name: str,
    tele: str = "LAT",
    start: str = "2023-06-08 00:00:00",
    stop: str = "2023-06-09 00:00:00",
):
    logger.info(f"Running stage 1 for %s, Offsets are", tube)
    offset_az, offset_el, tube_radius = get_wafer_offset_func(tube)

    schedule_file = Path("schedules") / f"schedule_{tube}_{sso_name}.txt"
    toast_ground_schedule_func(
        schedule_file,
        offset_az,
        offset_el,
        tube_radius,
        tele=tele,
        start=start,
        stop=stop,
        sso_name=sso_name,
    )


def stage2(
    band_name: str,
    tube: str,
    sso_name: str,
) -> None:
    logger.info(
        f"Running stage 1 for %s %s %s, Offsets are",
        band_name,
        tube,
        sso_name,
    )

    if tube in ("c1", "i5") and band_name in ("f230", "f290"):
        fsample = 200
    elif tube in ("i1", "i3", "i4", "i6") and band_name in ("f090", "f150"):
        fsample = 200
    elif tube in ("o6") and band_name in ("f030", "f040"):
        fsample = 60
    else:
        raise ValueError(f"Unknown tube/band combination: {tube}/{band_name}")
    logger.info(f"Sampling frequency is set to {fsample} Hz")

    schedule = Path("schedules") / f"schedule_{tube}_{sso_name}.txt"
    beam_file = get_beam_file("LAT", band_name)
    run_one(
        tele="LAT",
        band_name=band_name,
        tube=tube,
        sso_name=sso_name,
        fsample=fsample,
        schedule=schedule,
        beam_file=beam_file,
        ntask=1,
    )


def main(
    band_name: str,
    tube: str,
    sso_name: str,
) -> None:
    """Run the planet sims pipeline.

    :param band_name: Band name, e.g. f030 f040 f090 f150 f230 f290
    :param tube: Tube name, e.g. c1 i1 i5 i4
    :param sso_name: Name of the Solar System Object, e.g. Uranus Saturn Mars Jupiter
    """
    stage1(tube, sso_name)
    stage2(band_name, tube, sso_name)


if __name__ == "__main__":
    defopt.run(main, strict_kwonly=False)
