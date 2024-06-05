from typing import Optional

import numpy as np


def random_seed(meta_seed: Optional[int] = None) -> int:
    """Generate a RNG seed for the simulation engine.

    Used to generate a simulation seed for the user if they haven't specified
    one themselves.

    Parameters
    ----------
    meta_seed : Optional[int], optional
        Seed used to initialize the RNG that will itself be used to
        pseudo-randomly generate the simulation seed. If ``None`` (the default),
        unpredictable entropy from the OS is used in place of a ``meta_seed``.
        (see `docs`_ for ``numpy.random.default_rng``).

    Returns
    -------
    int
        Integer seed in range [0, 2**64).

    .. _docs: https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng  # noqa

    Notes
    -----
    Generated seeds can take any value in the range that can be represented by a
    64-bit unsigned integer, matching the range of seed values that FRED can
    accept as input.
    """
    return int(np.random.default_rng(meta_seed).integers(0, 2**64, dtype=np.uint64))
