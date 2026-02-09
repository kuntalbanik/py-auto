#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import platform
import subprocess


def ping_host(ip: str) -> None:
    param = "-n" if platform.system().lower() == "windows" else "-c"
    # print(ip, param)

    try:
        result = subprocess.run(
            ["ping", param, "2", ip],
            capture_output=True,
            text=True,
            check=False,  # Do not raise an exception for non-zero exit codes
        )
        result = str(result).lower()
        loss_track = (
            "request timed out" in result
            or "general failure" in result
            or "destination host unreachable" in result
        )

        if not loss_track:
            return True

    except Exception:
        return False


def expand_ip_range(ip_range: str) -> list:
    try:
        base, rng = ip_range.rsplit(".", 1)  # 192.168.1  &  1-254 spliting
        base_ex = base.split(".")
        for bs in base_ex:
            if len(bs) > 3 or int(bs) > 254:
                raise ValueError

        start, end = rng.split("-")
        start, end = int(start), int(end)

        if start and end > 254:
            raise ValueError

        return [f"{base}.{i}" for i in range(start, end + 1)]

    except Exception:
        return []
