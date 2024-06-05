from typing import Optional

from pydantic import BaseModel


class SynthPop:
    """An Epistemix synthetic population.

    Notes
    -----
    Currently this class is used to specify the synth pop locations for a given
    simulation run. Over time, methods will be added to support querying the
    synth pop independently of any particular run, analogously to the existing
    `epx-pop`_ package.

    .. _epx-pop: https://github.com/Epistemix-com/epx-pop/blob/main/epxpop/pop.py

    Parameters
    ----------
    name : str
        The name of a valid synthetic population, e.g. ``US_2010.v5``.
    locations : str
        List of location names within the specified synthetic population, e.g.
        ``["Allegheny_County_PA", "Jefferson_County_PA"]``.

    Attributes
    ----------
    name : str
        The name of a valid synthetic population, e.g. ``US_2010.v5``.
    locations : str
        List of location names within the specified synthetic population, e.g.
        ``["Allegheny_County_PA", "Jefferson_County_PA"]``.
    """

    def __init__(self, name: str, locations: Optional[list[str]]):
        self.name = name
        self.locations = locations

    def __repr__(self) -> str:
        return f"SynthPop(name={self.name}, locations={self.locations})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, SynthPop):
            return False
        if (self.name == other.name) and (self.locations == other.locations):
            return True
        return False


class SynthPopModel(BaseModel):
    """Data interchange helper for synthetic population objects.

    This is in the format recognized by the /run endpoint, which differs
    slightly from the ``epx.synthpop.SynthPop`` class that is part of the
    user-facing API.

    Attributes
    ----------
    version : str
        Synthetic population version, e.g. ``US_2010.v5``
    locations : list[str]
        List of location names within the specified synthetic population, e.g.
        ``["Allegheny_County_PA", "Jefferson_County_PA"]``.
    """

    version: str
    locations: list[str]

    @staticmethod
    def from_synth_pop(synth_pop: SynthPop) -> "SynthPopModel":
        return SynthPopModel(
            version=synth_pop.name,
            locations=synth_pop.locations,
        )

    def as_synth_pop(self) -> SynthPop:
        return SynthPop(
            name=self.version,
            locations=self.locations,
        )
