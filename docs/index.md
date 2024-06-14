<!-- # MolTopolParser -->
<style>
.hidden-title {
    display: none;
}
</style>

<h1 class="hidden-title">MolTopolParser</h1>

<div class="grid" markdown>
  ![MolTopolParser Logo](/img/mtp-logo-with-text.jpeg){ align=left style="width:250px"}
</div>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![Build Status](https://github.com/xinmengbcr/MolTopolParser/actions/workflows/build.yml/badge.svg)
[![codecov](https://codecov.io/github/xinmengbcr/MolTopolParser/graph/badge.svg?token=9K93F2PXVW)](https://codecov.io/github/xinmengbcr/MolTopolParser)
[![PyPI version](https://badge.fury.io/py/moltopolparser.svg)](https://badge.fury.io/py/moltopolparser)


**MolTopolParser**, abbreviated for *Molecular Topology Parser*, 
is a lightweight Python package designed to access, validate and process file 
or data used in various molecular simulation and modeling software.

- Full code on [github](https://github.com/xinmengbcr/MolTopolParser).

- [Installing](install.md) is simple: `pip install moltopolparser`

- Light dependences:
    - [pydantic](https://pypi.org/project/pydantic/)
    - [numpy](https://pypi.org/project/numpy/)
   

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

## How does it work

MolTopolParser provides a **three-level data abstraction model** to manage the hierarchical data.

> ADD DETAILS


Let's see one example of hierarchical structure formats from **Gromacs**. 
!!! example 
    === "Demo Gromacs Topologies"
        
        ```bash 
        $ tree membrane-martini-charmmgui/
        membrane-martini-charmmgui/
        ├── step5_charmm2gmx.pdb
        ├── system.top
        └── toppar
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

    === "martini_v2.2.itp"
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
        P5 	    5 	    1 	0.24145E-00 	0.26027E-02 ; supra attractive
        SP5 	SP5 	1 	0.10620E-00 	0.67132E-03 ; 75supra attractive, s=0.43
        ...

        [ moleculetype ]
        ; molname  	nrexcl
        W 	    	1

        [ atoms ]
        ;id 	type 	resnr 	residu 	atom 	cgnr 	charge
        1 	P4 	1 	W 	W 	1 	0 
        ...

        ```
    === "martini_v2.0_lipids_all_201506.itp"
        ```text
        [moleculetype]
        ; molname      nrexcl
        DAPC          1

        [atoms]
        ; id 	type 	resnr 	residu 	atom 	cgnr 	charge
        1 	Q0 	 1 	DAPC 	NC3 	 1 	1.0 	
        2 	Qa 	 1 	DAPC 	PO4 	 2 	-1.0 	
        ...
        [bonds]
        ;  i  j 	funct 	length 	force.c.
        1  2 	1 	0.47 	1250 
        ...
        [angles]
        ;  i  j  k 	funct 	angle 	force.c.
        2  3  4 	2 	120.0 	25.0 	
        ...
        ```


<!-- 
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

``` -->




<!-- ## Concepts  -->

<!-- ## Why MolTopolParser -->

<!-- ## Dependencies -->
<!-- * [pydantic](https://pypi.org/project/pydantic/) -->
<!-- * [numpy](https://pypi.org/project/numpy/) -->
 

<!-- ## Example -->
<!-- > pass  -->