# MolTopolParser 

## Guidelines
***Purpose of the Modules***
1. Direct Data Mapping:
The modules are designed to map data directly to files.
2. Data Validation and Type Checking: 
Ensuring that data conforms to expected formats and types.

***Design Considerations***
1. Data-Oriented Classes:
Focus on creating classes that are structured around data rather than
entities with file attributes.
2. Simplicity for Integration:
Avoiding entity classes with files as attributes to maintain simplicity
and facilitate the use of these classes with other tools.
All data classes are exposed directly to the user.

***Three Levels of Data Definition***

- Level 1: Base Data:

Description: Classes at this level represent individual lines of data.
Purpose: Focuses on the smallest unit of data, providing direct mapping and validation for each line.

- Level 2: Aggregation Data:

Description: Classes at this level represent sections of lines.
Purpose: Groups lines into meaningful sections for easier management and processing.

- Level 2: Aggregation-File Data:

Description: Classes at this level represent the entire file, without additional attached data.
Purpose: Manages the file as a complete entity, ensuring the integrity and structure of the whole file.

- Level 3: Summarization Data:

Description: Classes at this level represent summarized information of the entire content.
Purpose: Provides an entry point to access the whole involved content.



***dependencies***
- pydantic 
- numpy 

***test***
- make installable: prepare setup.py; pip install -e .
- example test command line: pytest tests/test_gmx.py -v -s


***setup for developing*** 
```text
cd MolTopolParser
python -m venv .venv 
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```


