from epx.synthpop import SynthPop


def test_synthpop_repr():
    s = SynthPop("US_2010.v5", ["Allegheny_County_PA", "Jefferson_County_PA"])
    assert s.__repr__() == (
        "SynthPop(name=US_2010.v5, "
        "locations=['Allegheny_County_PA', 'Jefferson_County_PA'])"
    )


def test_synthpop_eq():
    s1 = SynthPop("US_2010.v5", ["Allegheny_County_PA", "Jefferson_County_PA"])
    s2 = SynthPop("US_2010.v5", ["Allegheny_County_PA", "Jefferson_County_PA"])
    s3 = SynthPop("US_2010.v5", ["Allegheny_County_PA"])
    assert s1 == s2
    assert s1 != s3
