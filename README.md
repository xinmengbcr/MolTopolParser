<a href="https://github.com/xinmengbcr/MolTopolParser/">
  <img src="https://github.com/xinmengbcr/MolTopolParser/blob/main/docs/img/mtp-logo-with-text.jpeg?raw=true" width="250" title="Molecular Topology Parser">
</a>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![Build Status](https://github.com/xinmengbcr/MolTopolParser/actions/workflows/build.yml/badge.svg)
[![codecov](https://codecov.io/github/xinmengbcr/MolTopolParser/graph/badge.svg?token=9K93F2PXVW)](https://codecov.io/github/xinmengbcr/MolTopolParser)
[![PyPI version](https://badge.fury.io/py/moltopolparser.svg)](https://badge.fury.io/py/moltopolparser)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)


**MolTopolParser**, abbreviated from Molecular Topology Parser, is a lightweight, open-source Python package designed for accessing, validating, and processing files or data from various molecular simulation and modeling software. It simplifies interfacing between different simulation software and is pivotal in building computational pipelines for molecular simulations.

## Installation 

### Requirements

- Python 3.6 or newer

- pip package manager

### Quick Start

To install MolTopolParser, run the following command:

``` bash 
pip install moltopolparser
```

### Dependencies
MolTopolParser requires the following Python packages:

- [pydantic](https://pypi.org/project/pydantic/)
- [numpy](https://pypi.org/project/numpy/)

These dependencies are automatically installed during the MolTopolParser installation process.
   

## Features

- **Modular Design**: Structured around specific file formats from various simulation software, enhancing maintainability and scalability.

- **Pydantic Dataclasses**: Ensures robust data validation and type checking across the package.

- **Parsing as Class Methods**: Facilitates easy access to and manipulation of simulation files through well-defined class methods.

- **Exposed Modules and Dataclasses**: Enables advanced users to extend functionality or integrate with other tools.


## When To Use

MolTopolParser is designed for developers to manage hierarchical data structures commonly used in molecular simulations.
It provides a robust foundation for building advanced simulation tools and pipelines.

### Use Cases:

- Accessing and manipulating simulation files beyond mere coordinate data.

- Interfacing between different molecular simulation software.

- Building and managing computational pipelines.

### Not Suitable For:

- Simple parsing of structural data.

- Basic analysis of simulation outputs. (Consider using [Biopython ](https://biopython.org/), [MDAanalysis](https://www.mdanalysis.org/) etc.)


## Usage Examples

### Parsing Gromacs Files

```python
import moltopolparser as mtp

# Validate base data directly
atom_data = {
    "id": 10, "atom_type": "C", "resnr": 100,
    "residu": "UREA", "atom": "C1", "cgnr": 1, "charge": -0.683,
}
atom = mtp.gmx.MolTopAtom(**atom_data)
print(atom.charge)

# Parsing a single .gro file
gro_file = '../tests/data/gmx/two_water.gro'
gro = mtp.gmx.GroFile.parser(gro_file)
print(gro.box_size)

# Parsing and accessing a top file
top_file = '../tests/data/gmx/membrane-martini-charmmgui/system.top'
sys_top = mtp.gmx.Topology.parser(top_file)
print(sys_top.system)

sys_top.pull_forcefield()
print(sys_top.forcefield.atomtypes[0])  # Output: name='P5' at_num=None mass=72.0 charge=0.0 ptype='A' sigma=0.0 epsilon=0.0

sys_top.pull_molecule_topologies()
print(sys_top.molecule_topologies[0])
```



## Contributing
We encourage contributions from the community! Whether you are fixing bugs, proposing new features, or improving the documentation, your help is welcome.

- For Beginners
Submit [issue requests](https://github.com/xinmengbcr/MolTopolParser/issues) for bugs or feature suggestions.

- For Developers
Read the [concepts.md](https://moltopolparser.bocores.com/concepts/) and follow our [Developer's Guidence](https://moltopolparser.bocores.com/developer/) to understand how to set up your environment and contribute code.


## Versioning and Changelog
For details on the latest changes and version history, please refer to the full [Change Log](https://github.com/xinmengbcr/MolTopolParser/blob/main/CHANGELOG.md) on GitHub.

## License
MolTopolParser is released under the Apache License. See the [LICENSE](https://github.com/xinmengbcr/MolTopolParser/blob/main/LICENSE) file for more details.

---