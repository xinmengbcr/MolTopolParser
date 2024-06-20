# How does it work - Concepts

There could be various type of files involved in a molecular simulation project,
for example in a molecular dynamics simulation project, there should be a coordinate
file storing the atomic coordinates as the initial structure, a topology file contains
system information, force field files storing the force field parameters, and so on.


<div class="grid" markdown>
  ![Concepts Illustration](/img/illustration-components.pdf){ align=center style="width:900px"}
</div>



## 1. Components and Composition

An effcient way to think of all the files as composition of blocks of well-defined information.
__Taking the concept in React__, a meaningful block can be defined in to a __component__. Then a developer 
justs needs to think how to classify and organisig these components.

MolTopolParser is designed with a composition focus and provides an easy way to organise, access, validate and
manipulate these blocks of information. 



## 2. Three Order Component Model 

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


## 3. Component Behaviour 

The basic data flow logic follows: 

  - **Declaration and Organization**: Top-Down.
  - **Acquisition and Validation**: Bottom-Up.

When parsing happens, the top level always do *shallow* parsing,
and pass the cotent to lower level's classmethod to do the *deep* parsing. 
With such parsing tasks delegation, the top levels can more focus on 
data organisation. 
Such property passing from parent to child component is 
vital in MolTopolParser. 

In the TOC model:

  - **Summary** level's classmethod acts as the entry point for the entire `content`. 
after finishing simple parsing for *mandatory* properties, it will 
return a component instance. 

  - The instance can pass the `content` to classmethods at the **Aggregation** level 
and delegate the parsing task. 

  - Such logic continues in between  **Aggregation** and **Base** levels. 

--- 

!!! note
    Please continue to read the [Developer's Guidence](developer.md) for implementation detailed, where
    we show the anatomy of the `gmx` module. 

--- 




