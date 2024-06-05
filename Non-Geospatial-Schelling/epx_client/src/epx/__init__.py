__version__ = "0.1.2"
from epx.job import Job, ModelConfig, ModelConfigSweep
from epx.run import Run, RunParameters
from epx.synthpop import SynthPop

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
