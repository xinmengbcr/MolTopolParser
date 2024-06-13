# MolTopolParser

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![Build Status](https://github.com/xinmengbcr/MolTopolParser/actions/workflows/build.yml/badge.svg)
[![codecov](https://codecov.io/github/xinmengbcr/MolTopolParser/graph/badge.svg?token=9K93F2PXVW)](https://codecov.io/github/xinmengbcr/MolTopolParser)
[![PyPI version](https://badge.fury.io/py/moltopolparser.svg)](https://badge.fury.io/py/moltopolparser)


**MolTopolParser**, abbreviated for *Molecular Topology Parser*, 
is a lightweight Python package designed to access, validate and process file 
or data used in various molecular simulation and modeling software.
Full code on [github](https://github.com/xinmengbcr/MolTopolParser).


[Installing MolTopolParser](install.md) is as simple as: `pip install moltopolparser`

Light dependences:

* [pydantic](https://pypi.org/project/pydantic/)

* [numpy](https://pypi.org/project/numpy/)
 

## When To Use
MolTopolParser is designed for developers to manage hierarchical data 
structures commonly used in molecular simulations.
It focuses on providing a robust foundation for building advanced 
simulation tools and pipelines.

!!! Success "Yes"
    - access simulation files beyond coordinates 
    - interfacing different simulation softwares
    - build a computional pipline

!!! Warning "No"
    - only need to parse structure
    - perform analysis over simulation output. 

    There are other more suitable packages like:
    [Biopython ](https://biopython.org/), [MDAanalysis](https://www.mdanalysis.org/)..

## Three-level data abstraction model
MolTopolParser provides a **three-level data abstraction model** to manage the hierarchical data.


## How does it work

Let's see the hierarchical structure formats in **Gromacs** molecular dynamics simulation software. 
!!! example 
    === "Demo Gromacs Topologies"
        
        ```bash 
        $ tree membrane-martini-charmmgui/
        membrane-martini-charmmgui/
        ├── step5_charmm2gmx.pdb
        ├── system.top
        └── toppar
            ├── martini_v2.0_ions.itp
            ├── martini_v2.0_lipids_all_201506.itp
            └── martini_v2.2.itp
        ```

        Martini2 from CharmmGUI (1)
        { .annotate }

        1.  available at [./tests/data/gmx](https://github.com/xinmengbcr/MolTopolParser/tree/main/tests/data/gmx)


    === "system.top"
        ```text
        #include "toppar/martini_v2.2.itp"
        #include "toppar/martini_v2.0_lipids_all_201506.itp"
        #include "toppar/martini_v2.0_ions.itp"

        [ system ]
        ; name
        Martini system

        [ molecules ]
        ; name        number
        DOPC 2
        DPPC 1
        ...
        CL 9
        ```

    === "toppar/martini_v2.2.itp"
        ```text

        [ defaults ]
        1 1

        [ atomtypes ]
        ; polar type
        P5 72.0 0.000 A 0.0 0.0
        P4 72.0 0.000 A 0.0 0.0
        ...

        [ nonbond_params ]
        ; i j	funda c6 c12 
        ; self terms
        P5 	P5 	1 	0.24145E-00 	0.26027E-02 ; supra attractive
        SP5 	SP5 	1 	0.10620E-00 	0.67132E-03 ; 75supra attractive, s=0.43
        ...

        ```

        Phasellus posuere in sem ut cursus (1)
        { .annotate }

        1.  :woman_raising_hand: I'm an annotation as well!



```python
import moltopolparser as mtp

# Base data 
atom_data = {
        "id": 10,
        "atom_type": "C",
        "resnr": 100,
        "residu": "UREA",
        "atom": "C1",
        "cgnr": 1,
        "charge": -0.683,
    }
atom = mtp.gmx.MolTopAtom(**atom_data)
print(atom.charge)

```




<!-- ## Concepts  -->

<!-- ## Why MolTopolParser -->


<!-- ## Install -->
    <!-- pip install moltopolparser -->

<!-- ## Dependencies -->
<!-- * [pydantic](https://pypi.org/project/pydantic/) -->
<!-- * [numpy](https://pypi.org/project/numpy/) -->
 

<!-- ## Example -->
<!-- > pass  -->