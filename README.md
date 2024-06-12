<a href="https://github.com/xinmengbcr/MolTopolParser/">
  <img src="https://github.com/xinmengbcr/MolTopolParser/blob/main/docs/img/mtp-logo-with-text.jpeg?raw=true" width="250" title="Molecular Topology Parser">
</a>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
![Build Status](https://github.com/xinmengbcr/MolTopolParser/actions/workflows/build.yml/badge.svg)


**MolTopolParser**, abbreviated for *Molecular Topology Parser*, 
is a lightweight Python package designed to read and process file 
formats used in various molecular simulation and modeling software.

## Overview

Each module in MolTopolParser handles file formats specific to a type of software.
All file data is mapped to Pydantic dataclasses, ensuring data conforms to expected formats and types.
This approach provides a solid foundation for building simulation or pipeline tools,
while maintaining simplicity and facilitating integration with other tools.

## Features

- **Modular Design**: Each module corresponds to a specific software's file formats.
- **Pydantic Dataclasses**: Ensures data validation and type checking.
- **Class Methods for Parsing**: Includes parser functions as class methods for accessing and processing files.
- **Exposed Modules and Dataclasses**: All modules and their contained dataclasses are accessible.

## Data Hierarchy Model

MolTopolParser provides a **three-level data abstraction model** to manage the hierarchical nature of simulation data:

### Level 1: **Base Data**
Classes at this level represent individual lines in a file.
They focus on the smallest unit of data,
providing direct mapping and validation for each line.

### Level 2: **Aggregation Data** (or **Aggregation-File Data**)
Classes at this level represent a whole section of lines,
which could be stored in a standalone file.
They group Base Data lines into meaningful sections for easier management and processing.

### Level 3: **Summarization Data**
Classes at this top level usually correspond to an entry or summary file.
They gather all available data and provide access to the entire content.

## Data Flow Logic

- **Data Declaration and Organization**: From top-down.
- **Data Acquisition and Validation**: From bottom-up.

The parsing occurs at their corresponding data levels:

- **Summarization Level**: Acts as the entry point for the entire system/content.
  It calls and organizes data from the aggregation level.
- **Aggregation Level**: Handles the actual parsing. 
  It functions like a component in a framework,
  being called by the summarization level to parse and organize data.
- **Base Data Level**: Corresponds to the most basic data records.

Parser functions are included as class methods at the aggregation level,
while the summarization level calls these methods to parse and organize data.
Additionally, the aggregation level can include methods to convertor write out the data after parsing,
once the data is organized.



## User Guild 

Detailed installation and user guide, together with comprehensive example simulations are located in __link__

> example of calling the package module and dataclasses.



#### Installation 

```bash 
git clone FOLDER
pip install -r requirements.txt
pip install -e .
```

#### Dependencies
```text
pydantic 
numpy 
```

#### Setup for Developing
```bash
cd MolTopolParser
python -m venv .venv 
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
# run test
pytest tests/test_gmx.py -v -s
```

-----
