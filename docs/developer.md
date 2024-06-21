# Developer's Guide


!!! success "environment setup"

    ```bash
    # clone the repository 
    cd MolTopolParser
    python -m venv .venv 
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .
    # run test
    pytest tests/test_xxx.py -v -s
    ```



## Basic

Let's assume a new module `xxx` is going to be implememted to support a software in mind.

### Add a module file 

💡 In the `version 1` implementation, for simplicity, a module corresponds to a single `py` file. 

Inside the `MolTopolParser/moltopolparser` folder, a new file `xxx.py` should be created.
This module's info is also be registered in the `__init__.py` file, as shown via the `cat` below.


``` bash 
$ tree moltopolparser

moltopolparser
├── __init__.py
└── gmx.py
└── xxx.py  # <-

$ cat __init__.py

from . import gmx 
from . import xxx # <-

__all__ = ["gmx", "xxx"] # <-
```

### Add testing file 

Inside the `MolTopolParser/tests` folder, a new file `test_xxx.py` should be created.
When file `data` is necessary, the files should be allocted in a folder `MolTopolParser/tests/data/xxx`.


### Outline of a module file

There are five following sections in a module file:

- **Header and Imports** 🔥 If new packages need to be installed, 🚀 please also update the requirments in `setup.py` and `requirements.txt`
- **Level 1** Base dataclasses
- **Level 2**:  Aggregation dataclasses
- **Level 3**: Summary dataclasse(s)
- Helper functions


!!! quote "Five Sections"
    
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
    

The naming in the dataclasses are just made for demonstration. 
It is recommended to adpate the names that is more convinient and meaningful for the target. 


### Demo of the data flow

The usage usully starts with initializaiton of the Top level dataclass. 
The returned top-level dataclass intance contains the necessary information of system's and 
content that is included in the whole target files. 
To acess specific data, we just need to call the corresponding methods, e.g. `pull_*`. 

The following figure demonstrates the logic behind such operations. 
<div class="grid" markdown>
  ![Data-flow Illustration](/img/illustration-flow.pdf){align='center' style="width:500px "}
</div> 


## Practice with gmx.py 

Module `gmx.py` contains all the detailed implemenations. 
Via reading the code, all the concepts should be clarified. 

It is also recommended to copy the `gmx.py` to start a new module. 

Here is some demo of `gromacs` files that the module processes.


!!! quote "Example of Gromacs files"
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
    === "system.top  'entry file'"
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

    === "martini_v2.2.itp 'content file' "
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
    === "martini_v2.0_lipids_all_201506.itp 'content file'"
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

## Attention

- In the early verisons, all the dataclasses are directly inherating from `pydantic.BaseModel`.
We have not given *templated* dataclasses for each level, and there is some redundence could be reduced. 
Please submit an [issue request](https://github.com/xinmengbcr/MolTopolParser/issues) or implement directly if you want this to be improved.  

- API documentation is not made yet. If documentation of data formats needed, the corresponding `.md` file, e.g. `xxx_yyy.md` can put in the 
documentation folder `docs/data_reference` and add the record in the `mkdocs.yml` file. Run the following cmd to render the cocumentation: ```bash mkdocs serve```.

    !!! quote "example of modification in mkdocs.yml file"
        ```yml
        nav:
        - Getting Started: index.md
        - Concepts: concepts.md
        - Developer's Guide: developer.md
        - Data Reference:
            - gmx.MolTop: data_reference/gmx.MolTop.md
            - Name_eg_xxx.yyy: data_reference/xxx_yyy.md #<------ here 
        ```

- Submit an [issue request](https://github.com/xinmengbcr/MolTopolParser/issues) is always welcome 🚀