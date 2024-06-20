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
└── xxx.py  # <-----

$ cat __init__.py

from . import gmx 
from . import xxx # <-----

__all__ = ["gmx", "xxx"] # <-----
```

### Add testing file 

Inside the `MolTopolParser/tests` folder, a new file `test_xxx.py` should be created.
When file `data` is necessary, the files should be allocted in a folder `MolTopolParser/tests/data/xxx`.


### Outline of a module file

```py 
#####  Header information 
"""
Description
"""
#####  Import replying modules
import ... 
#####  Base level dataclasses 
class Base1(BaseModel):
    """
    Description
    """
    ### manditory attributes, e.g. 
    field_1: int = Field(..., description="x")
    ### optional attritues, e.g. 
    field_2: Optional[str] = Field(None, description="x")
    ### parse templates
    model_config = ConfigDict(
        json_schema_extra={
            ...
        }
    )
    #### classmethod for parsing 
    @classmethod
    def from_lines(cls, content: List[str]) -> Union["Base1", List["Base1"]]:
        ...

##### Aggregation level dataclasses
class Aggregation1(BaseModel):
    """
    Description
    """
    ### manditory attributes of BaseData e.g. 
    field_1: List[Base1] = Field(..., description="x")
    ### optional attritues of BaseData e.g. 
    field_2: Optional[List[Base2]] = Field(None, description="x")
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
        data_list = Base1.from_lines(content_lines) # <-- call the exact parsing classmethod at Base level 
        data = {
            field_1:data_list
        }
        return Aggregation1(**data) 

##### Summary level dataclasse(s)
class Summary(BaseModel):
    """
    Description
    """
    ### manditory attributes composed of AggregationData e.g. 
    field_1: List[Aggregation1] = Field(..., description="x")
    ### optional attritues composed of AggregationData e.g. 
    field_2: Optional[List[Aggregation2]] = Field(None, description="x")

    ### optional, collection of content to be passed when delegate the parsing tasks
    ### could be lines of data, or route of flles 
    inlines: Optional[List[str]] = Field( None,description="x",)
    
    ### parse templates
    model_config = ConfigDict(
        json_schema_extra={
            ...
        }
    )
    ### classmethod for shallow parsing, return cls instance 
    @classmethod
    def parser(cls, filename: str):
        ...
    
    ### instance method to delegate parsing tasks 
    def pull_example_field(self, ..)
    
```

1.  
2.  import requried modules. If necessary, please also update the requirments in `setup.py` and `requirements.txt`
3.  `Base` level dataclasses. 
4.  `Aggregation` level 
5.  `Summary` level 

