``epx``
=======

Python client for running simulations within the Epistemix Platform.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. _high_level_api:

High-level API
--------------

The high-level API is the primary interface for users of ``epx``. It is designed
to provide a convenient interface for configuring and executing collections
of simulations runs ('jobs') and managing their results. If there is something
you are trying to do that cannot be achieved using the high-level API, please
see documentation for the :ref:`low-level API <low_level_api>`.

The core concept in the high-level API is the **job**, implemented by the
``Job`` class. This represents a collection of simulation runs that share a
common FRED model entrypoint, FRED version, and compute instance size.

Configuring a job
^^^^^^^^^^^^^^^^^

In this example we will assume that you are developing a model in the
``~/my-model`` directory within the Platform IDE, and that the FRED model
entrypoint is ``~/my-model/main.fred``.

First, import the following:

.. code-block:: python

  from epx import Job, ModelConfig, ModelConfigSweep, SynthPop

Now, create an iterable of ``ModelConfig`` objects that define each run in our
job:

.. code-block:: python

    model_configs = [
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            start_date="2024-01-01",
            end_date="2024-01-31",
            model_params={"sample_parameter": 5},
            seed=12345,
        ),
        ModelConfig(
            synth_pop=SynthPop("US_2010.v5", ["Allegheny_County_PA"]),
            start_date="2024-02-01",
            end_date="2024-02-29",
            model_params={"sample_parameter": 10},
        ),
    ]

Note that the ``start_date`` and ``end_date`` parameters are optional and, if
not given, will default to the corresponding values given in the FRED model
code. The ``seed`` parameter is also optional and, if not given, a seed will be
randomly generated for you.

Often it is useful to run a job with a range of values for a given model--known
as a parameter sweep. This can be achieved using the ``ModelConfigSweep`` class
to configure the job, e.g.:

.. code-block:: python

    model_configs = ModelConfigSweep(
        synth_pop=[
            SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
            SynthPop("US_2010.v5", ["Allegheny_County_PA"])
        ],
        start_date=["2024-01-01"],
        end_date=["2024-01-31", "2024-02-29"],
        model_params=[{"sample_parameter": 5}, {"sample_parameter": 10}],
        n_reps=2,
    )

The above will generate configuration for a job with 16 runs: two repetitions
(each with different simulation seeds) of each combination of two synthetic
populations, a single start date, two end dates, and two values of the
``sample_parameter`` model parameter.

Whether the ``ModelConfig`` objects are specified explicitly (as in the first
example) or implicitly (as when using a ``ModelConfigSweep`` object), a ``Job``
is defined in the same way:

.. code-block:: python

    job = Job(
        "main.fred",
        config=model_configs,
        key="my-job",
        size="large",
        fred_version="11.0.1",
        results_dir="~/my-results",
    )

The optional ``size`` parameter enables configuration
of the compute instance size to use for the run. Permissible values are ``hot``
(the default) or any of the sizes listed in the
`Platform documentation <https://docs.epistemix.com/platform/pricing/#compute-credit-pricing>`_.
The optional ``fred_version`` parameter defaults to ``latest`` but can also be
used to specify a FRED ``10.1.1`` or ``11.0.1`` run. If not specified,
``results_dir`` defaults to ``~/results``.

Executing a job
^^^^^^^^^^^^^^^

To execute the job specified above, run

.. code-block:: python

    job.execute()

This will submit the job for execution. The current status of the job can be
checked by calling:

.. code-block:: python

    str(job.status)

Possible values are ``NOT STARTED``, ``RUNNING``, ``ERROR``, and ``DONE``.

Additionally, logs for the executing job can be accessed with:

.. code-block:: python

    job.status.logs

A summary of the job's runs that associates each parameter combinations with a
unique ID for the corresponding run can be accessed with:

.. code-block:: python

    job.run_meta

.. _viewing_results:

Viewing results
^^^^^^^^^^^^^^^

Once the job is complete, the results can be accessed through the
``job.results`` attribute. All FRED variable and file outputs are supported
using the methods detailed below. All methods return either a
``pandas.DataFrame`` or ``pandas.Series`` as appropriate.

State occupancy
"""""""""""""""

Counts of agents in each state can be accessed with ``run.results.state``. For a
given condition and state, the following count types are available:

* ``count``, the number of agents occupying the state at the end of each
  simulated day.
* ``new``, the number of agents entering the state at any time during each
  simulated day.
* ``cumulative``, the cumulative number of times any agent has entered the state
  since the beginning of the simulation, reported at the end of each simulated
  day.

For example, to access the cumulative count of agents that entered the
``MyState`` state of the ``MY_CONDITION`` condition, run:

.. code-block:: python

    job.results.state("MY_CONDITION", "MyState", "cumulative")

Population size
"""""""""""""""

A time series of the simulated population at the end of each simulated day
can be obtained with:

.. code-block:: python

    job.results.pop_size()

Epidemiological weeks
""""""""""""""""""""""

A time series mapping simulated days to epidemiological weeks can be obtained
with:

.. code-block:: python

    job.results.epi_weeks()

Dates
""""""

A mapping from simulated day numbers to calendar dates can be obtained with:

.. code-block:: python

    job.results.dates()

Print output
"""""""""""""

The output generated by calls to FRED's ``print`` action can be accessed with:

.. code-block:: python

    job.results.print_output()

CSV output
""""""""""

The output written to a ``.csv`` file by FRED's ``print_csv`` action can be
accessed with:

.. code-block:: python

    job.results.csv_output("my_file.csv")

File output
""""""""""""

The output written to a text file by FRED's ``print_file`` action can be accessed
with:

.. code-block:: python

    job.results.file_output("my_file.txt")


Numeric variable
""""""""""""""""

A time series of the value of a numeric variable can be obtained with:

.. code-block:: python

    job.results.numeric_var("my_numeric_var")

List variable
""""""""""""""

A time series of the value of a list variable can be obtained with:

.. code-block:: python

    job.results.list_var("my_list_var")

By using the optional ``wide=True`` argument, the output can be displayed in a
'wide' format, with each list element in a separate column:

.. code-block:: python

    job.results.list_var("my_list_var", wide=True)

Table variable
""""""""""""""

A time series of the value of a table variable can be obtained with:

.. code-block:: python

    job.results.table_var("my_table_var")

List table variable
"""""""""""""""""""

A time series of the value of a list table variable can be obtained with:

.. code-block:: python

    job.results.list_table_var("my_list_table_var")

By using the optional ``wide=True`` argument, the output can be displayed in a
'wide' format, with each list element in a separate column:

.. code-block:: python

    job.results.list_table_var("my_list_table_var", wide=True)

Revisiting a previously executed job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have configured and executed a job in a previous session and wish to
obtain a ``Job`` object for it (e.g. to access its results), this can be done
using the ``Job.from_key`` method, e.g.

.. code-block:: python

    job = Job.from_key("my-job")

Deleting a job
^^^^^^^^^^^^^^

Data for a previously executed job can be deleted by calling

.. code-block:: python

    job.delete()

By default, this method will prompt the user for confirmation before deleting
the job's results data. To suppress this prompt (e.g. to support programmatic
deletion of data for multiple job), pass ``interactive=False`` as an argument.

.. _low_level_api:

Low-level API
-------------

The low-level API is the core part of ``epx`` that interacts with the Sim Run
Service (SRS). Most users are expected to benefit most from use of the
high-level API (see :ref:`above <high_level_api>`). However, documentation and
usage of the low-level API will be useful for users developing complex or novel
use cases. We hope that support for such use cases will find their way into the
high-level API over time, and encourage users to submit pull requests to that
end.

The core concept in the low-level API is the **run**, implemented by the
``Run`` class. This represents a single realization of a FRED simulation. Runs
are uniquely identified by the path to their output directory in the user's
output directory (analogous to the path to a regular file in a file system).
When working with the low-level API, users are responsible for managing the
organization of run output directories (a key role of the high-level API is to
do this on behalf of the user).

Configuring a run
^^^^^^^^^^^^^^^^^

In this example we will assume that you are developing a model in the
``~/my-model`` directory within the Platform IDE, and that the FRED model
entrypoint is ``~/my-model/main.fred``.

First, import the following:

.. code-block:: python

  from epx import Run, RunParameters, SynthPop

Next, create a ``RunParameters`` object:

.. code-block:: python

    params = RunParameters(
        "main.fred",
        SynthPop("US_2010.v5", ["Jefferson_County_PA"]),
        start_date="2024-01-01",
        end_date="2024-01-31",
        model_params={"sample_parameter": 5},
    )

Here, ``sample_parameter`` is the name of a FRED numeric variable within the
model code that is being treated as a model parameter, and whose value is
specified within the ``RunParameters`` configuration.

Now, create a ``Run`` object:

.. code-block:: python

    run = Run(
        params,
        output_dir="~/my-results/my-run",
        size="large",
        fred_version="11.0.1",
    )

Here we specify that the simulation's results should be written to
``~/my-results/my-run``. The optional ``size`` parameter enables configuration
of the compute instance size to use for the run. Permissible values are ``hot``
(the default) or any of the sizes listed in the
`Platform documentation <https://docs.epistemix.com/platform/pricing/#compute-credit-pricing>`_.
The optional ``fred_version`` parameter defaults to ``latest`` but can also be
used to specify a FRED ``10.1.1`` or ``11.0.1`` run.

Executing a run
^^^^^^^^^^^^^^^

To execute the run specified above, run

.. code-block:: python

    run.execute()

This will submit the run for execution. The current status of the run can be
checked by calling:

.. code-block:: python

    str(run.status)

Possible values are ``NOT STARTED``, ``RUNNING``, ``ERROR``, and ``DONE``.

Additionally, logs for the executing run can be accessed with:

.. code-block:: python

    run.status.logs

Viewing results
^^^^^^^^^^^^^^^
Once the run is complete, the results can be accessed through the
``run.results`` attribute. The interface for accessing results for runs is
identical to the corresponding interface for accessing results for jobs. See
:ref:`corresponding documentation <viewing_results>` for the high-level API.

For example, to access the cumulative count of agents that entered the
``MyState`` state of the ``MY_CONDITION`` condition, *for a single run*, call:

.. code-block:: python

    run.results.state("MY_CONDITION", "MyState", "cumulative")

Revisiting a previously executed run
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have configured and executed a run in a previous session and wish to
obtain a ``Run`` object for it (e.g. to access its results), this can be done
using the ``Run.from_output_dir`` method, e.g.

.. code-block:: python

    run = Run.from_output_dir("~/my-results/my-run")

Deleting a run
^^^^^^^^^^^^^^

Data for a previously executed run can be deleted by calling

.. code-block:: python

    run.delete()

By default, this method will prompt the user for confirmation before deleting
results directory and its contents. To suppress this prompt (e.g. to support
programmatic deletion of data for multiple runs), pass
``interactive=False`` as an argument.

**Warning**

Users should be careful to ensure that the directory passed to the ``Run``
constructor is indeed the intended output directory for a run. A subsequent
call to ``Run.delete`` will recursively and irrecoverably delete this directory
and its contents.
