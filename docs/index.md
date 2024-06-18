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

- Feature: __Pydantic Dataclasses__ to ensure data validation and type checking.
  
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


## Example in Gromacs 


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

# Parse gro file 
gro_file = './tests/data/gmx/two_water.gro'
gro = mtp.gmx.GroFile.parse(gro_file)
print(gro.box_size)

# Parse top file 




# 
```





## How does it work - Concepts

<!-- 
When front-end developers talk about code, it’s most often in the context of designing interfaces for the web. And the way we think of interface composition is in elements, like buttons, lists, navigation, and the likes. React provides an optimized and simplified way of expressing interfaces in these elements. It also helps build complex and tricky interfaces by organizing your interface into three key concepts— components, props, and state. -->

There could be various type of files involved in a molecular simulation project,
for example in a molecular dynamics simulation project, there should be a coordinate
file storing the atomic coordinates as the initial structure, a topology file contains
system information, force field files storing the force field parameters, and so on.

<!-- 
Let's see one example of hierarchical structure formats from **Gromacs**. 
!!! example "Example of Gromacs simulation"
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



### 1. Components and Composition

An effcient way to think of all the files as composition of blocks of well-defined information.
__Taking the concept in React__, a meaningful block can be defined in to a __component__. Then a developer 
justs needs to think how to classify and organisig these components.

MolTopolParser is designed with a composition focus and provides an easy way to organise, access, validate and
manipulate these blocks of information. 

<div class="grid" markdown>
  ![Concepts Illustration](/img/illustration-components.pdf){ align=center style="width:900px"}
</div>


### 2. Three Order Component Model 

MolTopolParser utilizes a Three Order Component (TOC) data abstraction model.
It covers a basic hierachy data structure, and avoids uncessary layers. 
Although there is no limiation when going to higher ordres of hierachy. 
Likley, when using this tool for further developing, higher orders will be revolked. 

- Level 1: **Base**
Classes defined at this level represent individual lines. They
focus on the smallest unit of data, providing
direct mapping and validation for each line.

- Level 2: **Aggregation**
Classes at this level represent whole sections of lines, 
which could be stored in a standalone file.
They group `Base` components 
into meaningful sections for easier management and processing.

- Level 3: **Summary**
Classes at this top level usually correspond to an entry or summary file.
They are organising all the `Aggregation` components together and provide access to the entire content
to users. 


### 3. Component Behaviour 

The basic data flow logic follows: 

  - **Declaration and Organization**: Top-Down.
  - **Acquisition and Validation**: Bottom-Up.

When parsing happens, the top level always do *shallow* parsing,
and pass the cotent to lower level's classmethod to do the *deep* parsing. 
With such parsing tasks delegation, the top levels can more focus on 
data organisation. 
Such property passing from parent to child component is 
vital in MolTopolParser. 

In our TOC model: 
:one: **Summary** level's classmethod acts as the entry point for the entire `content`. 
after finishing simple parsing for *mandatory* properties, it will 
return a component instance. :two: The instance can pass the `content` to classmethods at the **Aggregation** level 
and delegate the parsing task. :three:  Similarly, the same logic happens in between  **Aggregation** and **Base** levels. 



<!-- ## Concepts  -->

<!-- ## Why MolTopolParser -->

<!-- ## Dependencies -->
<!-- * [pydantic](https://pypi.org/project/pydantic/) -->
<!-- * [numpy](https://pypi.org/project/numpy/) -->
 

<!-- ## Example -->
<!-- > pass  -->