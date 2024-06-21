# How does it work - Concepts

Understanding the underlying principles and architecture of MolTopolParser is essential for both using and contributing to the package. This section explains the types of files involved in molecular simulation projects, the design principles of MolTopolParser, and the data abstraction model it uses.


In molecular dynamics simulations, several types of files are typically used, each serving a specific purpose:

- **Coordinate Files**: Store the initial atomic or molecular coordinates that define the structure of the system.

- **Topology Files**: Contain detailed system information, including the types of particles and their interactions.

- **Force Field Files**: Define the forces applied to the particles in the system, specifying parameters such as bond lengths, angles, and torsional angles.
These files are critical for setting up and running molecular simulations accurately.


<div class="grid" markdown>
  ![Concepts Illustration](/img/illustration-components.pdf){ align=center style="width:900px"}
</div>



## Components and Composition

An efficient way to think of all the files is as a composition of blocks of well-defined information.
Similar to the concept in React, a meaningful block can be defined into a component. 
Then, a developer just needs to classify and organize these components.

MolTopolParser is designed with a composition focus, providing an easy way to organize, access, 
validate, and manipulate these blocks of information.

## Three-Order Component Model (TOC)

The TOC model simplifies data handling by categorizing data into three hierarchical levels:

- **Level 1: Base Classes** - These classes map directly to individual data entries, such as a single atom or bond. They provide immediate validation and data encapsulation.
- **Level 2: Aggregation Classes** - These classes manage groups of base components, such as all atoms in a molecule or all molecules in a system, facilitating operations on collections of components.
- **Level 3: Summary Classes** - At the highest level, these classes provide a summary or an overview of entire datasets or simulation setups, integrating multiple aggregation classes.



## Component Behaviour 

MolTopolParser operates on a clear data flow principle:

  - **Declaration and Organization**: Data structures are defined and organized from the top down, starting with the most comprehensive views
  
  - **Acquisition and Validation**: Data is parsed and validated from the bottom up, ensuring integrity at each step of the data structure

## Parsing Mechanism

When parsing data:

- **Shallow Parsing**: Top-level components perform shallow parsing to recognize data structures without delving into details.
  
- **Deep Parsing**: Detailed parsing tasks are delegated to lower levels, allowing higher-level components to remain abstract and focused on structure.
This method of delegation ensures efficiency and maintains clarity in data handling, avoiding redundancy and confusion in complex datasets.


## Further Reading

To understand how these concepts are implemented in MolTopolParser, please refer to the [Developer's Guidence](developer.md). This guide includes detailed examples and explanations of each component level and offers insight into extending MolTopolParser's capabilities.

---


