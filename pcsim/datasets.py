"""Instance loaders."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_jld(path: str | Path) -> tuple[list[int], list[int]]:
    """Read (charging, operation) from a Julia JLD file with a 2 x n matrix `D`.

    Row 1 of `D` holds charging times, row 2 operational times (files in
    legacy/waitingtime/*/). JLD is HDF5, so h5py reads it; Julia stores the
    matrix column-major, which h5py may expose transposed.
    """
    import h5py

    with h5py.File(path, "r") as f:
        d = np.array(f["D"])
    if d.shape[0] != 2:
        d = d.T
    return [int(v) for v in d[0]], [int(v) for v in d[1]]
