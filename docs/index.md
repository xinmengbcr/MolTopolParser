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
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)


**MolTopolParser**, abbreviated for *Molecular Topology Parser*, 
is a lightweight Python package designed to access, validate and process file 
or data used in various molecular simulation and modeling software.
  
- Full code on [github](https://github.com/xinmengbcr/MolTopolParser).

- [Installing](install.md) is simple: `pip install moltopolparser`

- Light dependences:
    - [pydantic](https://pypi.org/project/pydantic/)
    - [numpy](https://pypi.org/project/numpy/)
   

## Features

- Modular Design: Each module corresponds to a specific software's file formats.

- Pydantic Dataclasses: Ensures data validation and type checking.

- Class Methods for Parsing: Includes parser functions as class methods for accessing and processing files.

- Exposed Modules and Dataclasses: All modules and their contained dataclasses are accessible.


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


## Example of parsing Gromacs files 


```python
import moltopolparser as mtp

# Base data direct validation
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

# Access via parsing a single file
gro_file = '../tests/data/gmx/two_water.gro'
gro = mtp.gmx.GroFile.parser(gro_file)
print(gro.box_size)

# Access via parsing top files, see example file below
top_file = '../tests/data/gmx/membrane-martini-charmmgui/system.top'
sys_top = mtp.gmx.Topology.parser(top_file)
print(sys_top.system) 

sys_top.pull_forcefield()
print(sys_top.forcefield.atomtypes[0]) 
# -> name='P5' at_num=None mass=72.0 charge=0.0 ptype='A' sigma=0.0 epsilon=0.0

sys_top.pull_molecule_topologies()
print(sys_top.molecule_topologies[0])
```
<!-- 
!!! note "Example of Gromacs files"
    === "files"
        
        ```bash 
        $ tree membrane-martini-charmmgui/
        membrane-martini-charmmgui/
        ├── step5_charmm2gmx.pdb
        ├── system.top
        └── toppar
            ├── martini_v2.0_lipids_all_201506.itp
            └── martini_v2.2.itp
        ```
    === "system.top"
        ```text
        #include "toppar/martini_v2.2.itp"
        #include "toppar/martini_v2.0_lipids_all_201506.itp"
        #include "toppar/martini_v2.0_ions.itp"

        [ system ]
        Martini system

        [ molecules ]
        DOPC 2
        ...
        CL 9
        ```

    === "martini_v2.2.itp"
        ```text
        [ defaults ]
        1 1

        [ atomtypes ]
        P5 72.0 0.000 A 0.0 0.0
        ...
        
        [ nonbond_params ]
        ; i j	funda c6 c12 
        P5 	    5 	    1 	0.24145E-00 	0.26027E-02 ; supra attractive
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
 -->


## Contrubuting 

🚀  No support of your files? Pursuring of new features?

👍 We'd love you to contribute to MolTopolParser ! 

For beginner users, the easy way is just to directly submit an [issue request](https://github.com/xinmengbcr/MolTopolParser/issues).
For develepors, you can read the [Concepts](concepts.md) follow our [Developer's Guidence](developer.md) to get started. 

