# Getting Started

## Installing Prerequisite Software

[NumPy](http://www.numpy.org), [SciPy](http://www.scipy.org) and [matplotlib](http://matplotlib.org) should be installed in your Python environment. The packages are normally included with most Python bundles, such as [Anaconda](https://www.continuum.io/downloads) or [Canopy](https://store.enthought.com/downloads/#default).

### Windows

It is highly recommended to use a scientific python distribution on Windows, such as [Anaconda](https://www.continuum.io/downloads) or [Canopy](https://store.enthought.com/downloads/#default).

`SciPy` currently does not offer pre-built binary packages for Windows in the wheel format through PyPI. As a consequence, it cannot be properly installed via a regular `pip install` command.

As an alternative to scientific python distributions, a more lightweight installation is possible by combining the standard [Python release for Windows](https://www.python.org/downloads/windows/) with a selection of pre-built packages:

#### Python 3.6 (Recommended)

- [Python 3.6.1](https://www.python.org/downloads/release/python-361/) - Download `Windows x86-64 executable installer`
- [Numpy 1.13.0 + MKL](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) - Download `numpy‑1.13.0+mkl‑cp36‑cp36m‑win_amd64.whl`
- [SciPy 0.19.1](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy) - Download `scipy‑0.19.1‑cp36‑cp36m‑win_amd64.whl`

Launch the Python installer and install with all options selected (including `Add python.exe to Path`). Then, launch the following commands:

    pip install numpy‑1.13.0+mkl‑cp36‑cp36m‑win_amd64.whl
    pip install scipy‑0.19.1‑cp36‑cp36m‑win_amd64.whl
    pip install matplotlib

#### Python 2.7

- [Python 2.7.13](https://www.python.org/downloads/release/python-2713/) - Download `Windows x86-64 MSI installer`
- [Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266)
- [Numpy 1.13.0 + MKL](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) - Download `numpy‑1.13.0+mkl‑cp27‑cp27m‑win_amd64.whl`
- [SciPy 0.19.1](http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy) - Download `scipy‑0.19.1‑cp27‑cp27m‑win_amd64.whl`

Launch the Python installer and install with path option enabled (including `Add Python 3.6 to PATH`). Then, launch the following commands:

    pip install numpy‑1.13.0+mkl‑cp27‑cp27m‑win_amd64.whl
    pip install scipy‑0.19.1‑cp27‑cp27m‑win_amd64.whl
    pip install matplotlib

## MacOS / Linux

It is also recommended to use a scientific python distribution on MacOS and Linux, such as [Anaconda](https://www.continuum.io/downloads) or [Canopy](https://store.enthought.com/downloads/#default).

As a general rule, you should not alter the default Python installation shipped with the OS, but install and use a separate Python environment. Use your package manager to install a separate Python interpreter (`homebrew` on MacOS or `apt` on Debian/Ubuntu), and then install the necessary dependencies via `pip`:

    pip install numpy
    pip install scipy
    pip install matplotlib

## Installing Dependencies

In order to perform sensitivity analysis on building energy models, you will need the [SALib - Sensitivity Analysis Library](https://github.com/SALib/SALib) and the [PyBPS - Parametric Simulation Manager](https://github.com/dtavan/PyBPS) packages installed on your computer. Using pip, these libraries can be installed with the following command:

    pip install salib
    pip install pybps

Additionally, it is recommended to install `jupyter` to enable notebooks support

    pip install jupyter

## Sensitivity Analysis with TRNSYS

The methodology presented here was mainly developed to make it possible to perform sensitivity analysis on [TRNSYS](http://trnsys.com) models.

The example `examples\trnsys_sunspace` is based on one of the examples distributed with TRNSYS, and even works with the Demo version of TRNSYS 17 which [can be downloaded from the trnsys.com website](http://trnsys.com/demo/) (Windows only).

### Prepare a TRNSYS Project for Sensitivity Analysis

Any TRNSYS project can be setup for sensitivity analysis with `SALib`and `PyBPS`. However, it is necessary to follow a few steps to make it work.

#### Template Files

Once a TRNSYS project is set up and working properly (i.e., simulation runs without errors), parameters to be sampled during the sensitivity analysis should be identified.

Then, copies of the TRNSYS deck file (.dck) and eventually Building description file (.bui) should be made with the string `_Template` added to their filename. For example, the template files for the `trnsys_sunspace` example are `SunSpace-Shading_Template.dck` and `SunSpace_Template.bui`

Values of the parameters identified for sensitivity analysis should then be replaced by a search string that PyBPS will be able to replace by sampled values. **Parameter search strings should always be strings with a leading $ sign.**

As an example, here is the user defined constants section of the `SunSpace-Shading.dck`

    * User defined CONSTANTS
    CONSTANTS 5

    OVERHANG_PROJ = 1
    INF_RATE = 1.0
    T_HEAT = 20
    T_COOL = 25
    LIG_SCALE = 0.8

When converted to the `SunSpace-Shading_Template.dck` template file it becomes

    * User defined CONSTANTS
    CONSTANTS 5

    OVERHANG_PROJ = $OVERHANG_PROJ
    INF_RATE = $INF_RATE
    T_HEAT = $T_HEAT
    T_COOL = $T_COOL
    LIG_SCALE = $LIG_SCALE

**IMPORTANT!**

Do NOT use the following strings as parameter names, which are already used in TRNSYS input files

    $UNIT_NAME
    $MODEL
    $POSITION
    $LAYER

#### Parameter Ranges

For every single identified parameter (and corresponding search string) defined in the template files, there should be a corresponding line with min/max values in the parameter range file.

Parameter range files should always be CSV files with each line having the following format: PARAMETER, MIN_VALUE, MAX_VALUE

    OVERHANG_PROJ,0.6,1.4
    INF_RATE,0.6,1.4
    T_HEAT,19,21
    T_COOL,24,26
    LIG_SCALE,0.7,1

This range definition is sufficient for a simple sensitivity analysis, using the Morris method.
However, if using more advanced SA techniques (Sobol indices) or performing Uncertainty analysis, probability distributions must be associated with each parameter, which adds an additional step to the sampling pipeline and is not covered by this tutorial.

#### Model Output

`PyBPS` currently requires model outputs to be written to a single text file by a `Type46` *Printegrator* object, with the printing/integrating interval set to monthly output (-1 value).

Also, for better readability of results, it is highly recommended to convert all energy output variables to kWh (TRNSYS computes all energy-related variables in kJ) by dividing kJ outputs by a factor 3600.

By default, sensitivity analysis will be performed for all outputs found in the `Type46` output file (text file with .out extension). However, a particular output can be specified when running the analysis script (-Y option).

#### Project Data Files

ALL external TRNSYS project data file (such as weather file, or any other type of text file used by TRNSYS project as input) should be kept in the same folder (or eventually in a sub-folder) as the main TRNSYS project files (.tpf, .dck), and only RELATIVE PATHS should be used. Absolute paths won't work when launching parallel simulation runs.

For example, the Madrid weather file is contained in the `Weather` sub-folder of the `trnsys_sunspace` project folder and the path set in the `Type15` is `Weather\ES-Madrid-Barajas-82210.tm2`.

#### PyBPS Configuration

Check that the `Install_Dir` parameter for the simulation tool directory is set properly in the `pybps_config.ini` file located in the `examples\trnsys_sunspace` folder. By default, it is set for the TRNSYS17 Demo, but if you have a TRNSYS17 license, you should set the path properly, as shown below

    [TRNSYS]
    Install_Dir = C:\TRNSYS17 # Default installation directory for TRNSYS v17

## Perform Sensitivity Analysis

For now, the only type of sensitivity analysis demonstrated is the Morris method, which is one of the simplest yet most effective sensitivity analysis methods.

A script was created to make it possible to run a sensitivity analysis using the Morris method in a single step.

Once a TRNSYS project is set up as described in the previous section, just launch the `run-morris-sa.py` script (found in `scripts` folder). For example, the analysis of the `trnsys_sunspace` project can be launched with the following command:

    run-morris-sa.py ..\examples\trnsys_sunspace Parameter_Ranges.csv

Launching `run-morris-sa.py -h` gives hints regarding analysis options
