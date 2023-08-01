#!/usr/bin/env python

from pathlib import Path

import defopt


def gen_job(
    band_name: str,
    tube: str,
    sso_name: str,
    config_template: str,
) -> None:
    config_path = Path(f"{band_name}_{tube}_{sso_name}.ini")
    with config_path.open("w", encoding="utf8") as f:
        f.write(
            config_template.format(
                band_name=band_name,
                tube=tube,
                sso_name=sso_name,
            )
        )


def gen_jobs(
    config_template: Path,
) -> None:
    with config_template.open("r") as f:
        config_template_str = f.read()

    # Uranus, Saturn, and Jupiter
    for sso_name in ("Uranus", "Saturn", "Jupiter"):
        # c1, i1, and i4
        for tube in ("c1", "i1", "i4"):
            if tube in ("c1", "i5"):
                bands = ("f230", "f290")
            elif tube in ("i1", "i3", "i4", "i6"):
                bands = ("f090", "f150")
            elif tube in ("o6"):
                bands = ("f030", "f040")
            for band_name in bands:
                gen_job(
                    band_name,
                    tube,
                    sso_name,
                    config_template=config_template_str,
                )


if __name__ == "__main__":
    defopt.run(gen_jobs, strict_kwonly=False)
