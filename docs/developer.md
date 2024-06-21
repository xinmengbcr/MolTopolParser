# Developer's Guide

Welcome to the MolTopolParser developer's guide. 
This guide provides all the necessary information for setting up your development environment,
understanding the codebase, and contributing effectively to the project.

## Environment Setup

### Clone the Repository

Start by cloning the MolTopolParser repository to your local machine:

```bash
git clone https://github.com/your-username/MolTopolParser.git
cd MolTopolParser
```

### Create a Virtual Environment
It's recommended to create a virtual environment for development to manage dependencies cleanly:
```bash 
python -m venv .venv
source .venv/bin/activate
```
### Install Dependencies
Install all required dependencies using pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Run Tests
Ensure that all tests pass to verify your setup:
```bash
pytest tests -v -s
```

## Developing a New Module

If you are adding a new module to support a different simulation software, here's how to get started:

### Add a module file 

1.  **Create a new file** under the `moltopolparser` directory for your module, e.g., `xxx.py`.
2.  **Register the new module** in the `__init__.py` file:

```python
from . import xxx
__all__ = ['gmx', 'xxx']
```



### Define Data Classes

Organize your module using the Three-Order Component (TOC) model:

1. **Level 1 Base Data Classes** - Define data classes for the smallest data units.
2. **Level 2 Aggregation Classes** - Group base classes into meaningful sections.
3. **Level 3 Summary Classes** - Organize and manage entire file contents or complex data structures.

### Implement Parsing Functions

Add class methods for parsing data, validating, and possibly manipulating or transforming data.

### Testing Your Module
Create a testing file in the `tests` directory:

1. Structure: Place your test file, e.g., `test_xxx.py`.
2. Data Files: Store necessary data files under `tests/data/xxx/` for use in tests.

### Example Code Block
Here’s a simplified structure of what your module file might look like:

```python
# Header and Imports
"""
Module to parse and manage data from Software XXX
"""
import necessary_libraries # (1)

# Base dataclasses
class BaseClass:
    pass

# Aggregation dataclasses
class AggregateClass:
    pass

# Summary dataclasses
class SummaryClass:
    pass

# Additional helper functions if needed
```

1. If new packages need to be installed, please also update the `setup.py` and `requirements.txt` files 

## Understanding Data Access and Manipulation

MolTopolParser simplifies the process of working with molecular simulation files by providing structured data access 
through its class hierarchy. The process typically begins with the initialization of a top-level data class, 
which acts as a gateway to all underlying data associated with a simulation.

### Top-Level Dataclass Initialization
When you initialize the top-level dataclass, it constructs an instance that encapsulates all the necessary information
of the system and its related contents from the target files. 
This encapsulation allows for a structured and organized approach to accessing and manipulating the data:

```python
# Example of initializing a top-level dataclass
system_topology = SystemTopology(parser="path/to/topology_file.top")
```
### Accessing Data
Once the top-level class is initialized, specific data can be accessed by invoking corresponding 
methods defined within the class. These methods typically follow the naming convention `pull_*` to indicate that they 
retrieve specific types of data or perform certain operations to organize and validate data:
```python
# Example of accessing data using a method
system_topology.pull_forcefield()
system_topology.pull_molecules()
forcefield_data = system_topology.forcefield
molecules = system_topology.molecules
```

### Illustration 

The following figure demonstrates the Initialization and Access Procoesses based on a toy module file. 

<div class="grid" markdown>
  ![Data-flow Illustration](/img/illustration-flow.pdf){align='center' style="width:600px"}
</div> 

Here’s the toy module file:

!!! quote "Five Sections in a toye module file"
    
    === "Header and Imports"
        ```py 
        #####  Header information 
        """
        Description
        """
        #####  Import replying modules
        import ... 
        ```

    === "Level 1: Base dataclasses"
        ```py
        class Base1(BaseModel):
            """
            Description
            """
            ### attributes, e.g. 
            field_1: int = Field(..., description="x")
            ### parse templates
            model_config = ConfigDict(
                json_schema_extra={
                    ...
                }
            )
            #### classmethod for parsing 
            @classmethod
            def parser(cls, content: List[str]) -> Union["Base1", List["Base1"]]:
                ...
        class Base2 ...
        ```

    === "Level 2:  Aggregation dataclasses"
        ```py
        class Aggregation1(BaseModel):
            """
            Description
            """
            ### attributes of BaseData e.g. 
            field_1: List[Base1] = Field(..., description="x")
            field_2: List[Base2] = Field(..., description="x")
            ### parse templates
            model_config = ConfigDict(
                json_schema_extra={
                    ...
                }
            )
            ### classmethod parsing
            @classmethod
            def parser(cls, content_lines: Optional[List[str]] = None, content_files: Optional[List[str]] = None):
                """
                Parse the aggregation data from the content passed when it is called
                """
                data1_list = Base1.parser(content_lines) # <-- call the exact parsing classmethod at Base level 
                data2_list = Base2.parser(content_lines)
                data = {
                    field_1:data1_list
                    field_2:data2_list
                }
                return Aggregation1(**data) 
        ```

    ===  "Level 3: Summary dataclasse(s)"
        ```py
        class Summary(BaseModel):
            """
            Description
            """
            ### manditory attributes to initite  
            field_1: str = Field(..., description="x")
            ### attritues composed of AggregationData to be parsed e.g. 
            field_2: Optional[List[Aggregation1]] = Field(None, description="x")
            ### attritue, collection of content to be passed when delegate the parsing tasks
            ### could be lines of data, or route of flles 
            pass_content: Optional[List[str]] = Field( None,description="x",)
            
            ### parse templates
            model_config = ConfigDict(
                json_schema_extra={
                    ...
                }
            )
            ### classmethod for shallow parsing,
            ### obtain the  manditory attributes 
            ### and return a cls instance
            @classmethod
            def parser(cls, filename: str):
                ...
            
            ### instance method to delegate parsing tasks 
            def pull_field2(self)
                ### call aggregation level classmethod
                self.field_2 = Aggregation1.parser(self.pass_content)        
        ```
    === "Helper functions"
        ```py
        ### Helper functions e.g. 
        ### deployed to filter out commnets in content, 
        ### to locate range of data need to be passed. 
        ```

## Practice with gmx.py 

Module `gmx.py` contains all the detailed implemenations. 
Via reading the code, all the concepts should be clarified. 

It is also recommended to copy the `gmx.py` to start a new module. 


## Submitting Contributions

### Pull Requests

1. **Fork the repository** - Make a copy of the project on your GitHub account.
2. **Make your changes** - Work on your fork and make the changes you propose.
3. **Submit a pull request** - Open a pull request from your fork back to the main repository.

### Code Style and Review
Follow PEP 8 guidelines for Python code. Ensure your code is clean and well-documented.
All contributions will undergo a review process by core maintainers.



## Attention

### Early Version Data Structure Improvements

In the initial versions of MolTopolParser, all data classes inherit directly from `pydantic.BaseModel`. 
This implementation did not utilize *templated* data classes for each hierarchical level, 
leading to some redundancy that could be streamlined to enhance the package's efficiency and maintainability. 
If you encounter issues or have suggestions for improvements,
please do not hesitate to submit an [issue request]((https://github.com/xinmengbcr/MolTopolParser/issues))
or contribute directly by implementing enhancements.

### API Documentation
As of now, comprehensive API documentation has not been established for MolTopolParser.
For users requiring documentation of specific data formats, 
it is advised to create a markdown file, such as `xxx_yyy.md`, detailing the data structure and its usage. 
Place this file in the `docs/reference` directory.
To update the documentation site with this new information, 
add an entry to the `mkdocs.yml` file under the `Reference` section and use the `mkdocs serve` 
command to generate and view the documentation locally.

Example modification in `mkdocs.yml` file:

``` yml
nav:
  - Getting Started: index.md
  - Concepts: concepts.md
  - Developer's Guide: developer.md
  - Reference:
      - gmx.MolTop: reference/gmx.MolTop.md
      - Name_eg_xxx.yyy: reference/xxx_yyy.md #<------ here 
```
Run the following command to render the documentation:

``` bash
mkdocs serve
```

## Need Help?
If you encounter any problems or have questions while contributing,
please [open an issue](https://github.com/xinmengbcr/MolTopolParser/issues) on the GitHub repository.
