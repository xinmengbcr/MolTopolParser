"""
This module contains the classes and functions to parse Gromacs files.

"""
from typing import List, Optional

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class GroFileAtom(BaseModel):
    """
    Represents an atom in a Gromacs .gro file.
    Note:
    % This class contains vecolity components vx, vy, vz which are optional.
    % If they are not provided, they are set to 0.0.
    % Forces are not included in this class.
    """

    resid: int = Field(..., description="Residue ID")
    resname: str = Field(..., description="Residue name")
    atom_name: str = Field(..., description="Atom name")
    index: int = Field(..., description="Atom index")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    vx: float = Field(0.0, description="Velocity in X direction")
    vy: float = Field(0.0, description="Velocity in Y direction")
    vz: float = Field(0.0, description="Velocity in Z direction")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resid": 1,
                "resname": "H2O",
                "atom_name": "O",
                "index": 1,
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "vx": 0.0,
                "vy": 0.0,
                "vz": 0.0,
            }
        }
    )


class GroFile(BaseModel):
    """
    Represents a Gromacs .gro file.
    sys_name: str
    num_atoms: int
    gro_atoms: list of GroFileAtom
    box_size: np.array
    """

    sys_name: str = Field(..., description="System name")
    num_atoms: int = Field(..., description="Number of atoms")
    gro_atoms: List[GroFileAtom] = Field(..., description="List of atoms")
    box_size: List[float] = Field(..., description="Box size")

    # TBD: Add dump method to write the gro file, or convert to other formats


class Topology(BaseModel):
    """[ system ] and [ molecules ] section of the top file.
    example data:
    --------
    [ system ]
    Urea in Water

    [ molecules ]
    Urea    1
    SOL     1000
    --------
    """

    system: str = Field(..., description="System name")
    molecules: List[dict[str, int]] = Field(..., description="Molecules included")
    # molecule_topologies: Optional[List[MoleculeTopology]] = \
    # Field(..., description="Molecule topology")
    # atomtypes: Optional[List[str]] = Field(..., description="Atom types")

    # extra include force field files in the top file
    # shallow_include: Optional[List[str]] = Field(...,
    #  description="Include files")


def parse_gro_file(input_file: str) -> GroFile:
    """
    Parse a Gromacs .gro file and return a GroFile class instance.
    Example of Gro file:
    --------
    MD of 2 waters, t= 0.0
        6
        1WATER  OW1    1   0.126   1.624   1.679  0.1227 -0.0580  0.0434
        1WATER  HW2    2   0.190   1.661   1.747  0.8085  0.3191 -0.7791
        1WATER  HW3    3   0.177   1.568   1.613 -0.9045 -2.6469  1.3180
        2WATER  OW1    4   1.275   0.053   0.622  0.2519  0.3140 -0.1734
        2WATER  HW2    5   1.337   0.002   0.680 -1.0641 -1.1349  0.0257
        2WATER  HW3    6   1.326   0.120   0.568  1.9427 -0.8216 -0.0244
       1.82060   1.82060   1.82060
    ---------
    """
    _skip_lines = 2  # The first two lines are not atoms
    with open(input_file, encoding="utf-8") as f:
        lines = f.readlines()
        num_atoms = int(lines[1])
        box_size = np.array(
            lines[_skip_lines + num_atoms].strip("\n").lstrip().split(), dtype=float
        )
    gro_atoms: List[GroFileAtom] = []
    for line in lines[_skip_lines : _skip_lines + num_atoms]:
        line_length = len(line)
        atom_data = {
            "resid": int(line[:5]),
            "resname": line[5:10].strip(),
            "atom_name": line[10:15].strip(),
            "index": int(line[15:20]),
            "x": float(line[20:28]),
            "y": float(line[28:36]),
            "z": float(line[36:44]),
        }
        if line_length == 69:
            atom_data["vx"] = float(line[44:52])
            atom_data["vy"] = float(line[52:60])
            atom_data["vz"] = float(line[60:68])
        gro_atoms.append(GroFileAtom(**atom_data))
        if line_length not in (45, 69):
            raise ValueError(
                f"Gro file line not formatted correctly:\n"
                f"{line}"
                "The line length is {line_length} "
                "while it should be 45 for a gro file containing positions"
                "or 69 containing both positions and velocities."
            )
    return GroFile(
        sys_name=lines[0].strip("\n"),
        num_atoms=num_atoms,
        gro_atoms=gro_atoms,
        box_size=box_size.tolist(),
    )


def find_section_range(lines: List[str], section_name: str) -> tuple[int, int]:
    """
    Find the range of a section in the lines.
    """
    idx_section = [
        x for x in range(len(lines))
        if f"[ {section_name} ]" in lines[x].lower()
    ]
    idx_section_general = [x for x in range(len(lines))
                           if "[ " in lines[x].lower()]
    # start = idx_section[0]
    # try:
    #     end = idx_section_general[idx_section.index(start) + 1]  # next '[' idx
    #     # data_target = lines[start:end]
    # except IndexError:
    #     end = -1
    #     # data_target = lines[start:]  # Not data[start:-1]
    # print(idx_section, idx_section_general, start, end)
    return idx_section, idx_section_general


def parse_top_file_shallow(filename: str) -> tuple[dict[str, int], list[str]]:
    """
    Parse a Gromacs .top file and return a dictionary of the
    [ system ] and [ molecules ] section.

    Warnining: current version works with the file format from the
    Martini 2 force field from the Charmm-GUI server;
    Others to be added

    Example of Top file:
    --------
    #include "toppar/martini_v2.2.itp"
    #include "toppar/martini_v2.0_lipids_all_201506.itp"
    #include "toppar/martini_v2.0_ions.itp"

    [ system ]
    ; name
    Martini system

    [ molecules ]
    ; name        number
    DOPC 2
    DPPC 1
    DOPC 5
    --------

    General rule of searching a section in the file:
    SECTION_NAME = "system"
    Then the section is found by searching for the line
    "[ system ]" or other capitalized version of the section name.
    or with or without space with the brackets.

    The next none empty line that does not start with ;
    is the value of the section.
    """

    with open(filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
        # clean lines data, throw the lines that start with ; or empty lines
        lines = [
            line.strip() for line in lines if not line.startswith(";") and line.strip()
        ]
        # look for the section [ system ]
        idx_section, _ = find_section_range(lines, "system")
        system_name = lines[idx_section[0] + 1]
        # look for the section [ molecules ]
        





        top_data = {
            "system": system_name,
            "molecules": []
        }
        print(top_data)
        


# def load_martini_ff_vdw(itp_file):
#     """
#     2021-07-07 before, in all the load gmx itp files,
#     loop lines and break with empty line;
#     which requires no unnecessary gap lines
#     === Now then loop the until the next section  [ ] or end

#     target section: [ nonbond_params ]

#     """
#     itpVdwAtom_list = []

#     itpVdwPair_list = []
#     with open(itp_file,'r') as f:
#         data = f.readlines()
#         index_nonbond = [x for x in range(len(data)) if '[ nonbond_params ]' in data[x].lower()]
#         index_section = [x for x in range(len(data)) if '[ ' in data[x].lower()]
#         #print(index_nonbond)
#         #print(index_section)
#         start = index_nonbond[0] # section [ nonbond_params ]
#         try:
#             end   =  index_section[  index_section.index(start) + 1 ] # section next to [ nonbond_params ]
#             data_target = data[start:end]
#         except:
#             end   =  -1
#             data_target = data[start:] ### checked already that if put -1; then the last line -1 is not included
#         #print( start, end)

#         ############### access [ nonbond_params ] section
#         ### for line in data[start:end]: ## to index_pairs[0] or -1
#         for line in data_target:
#             ##print(line )
#             demoline = line.split()
#             #print(demoline)
#             if demoline: ### this is a list,  will filter the empty list, i.e. empty line
#                 #print(demoline)
#                 if gmx_record_match(demoline[0]):
#                     #print(demoline) ### test ok
#                     vdw_head   = demoline[0]
#                     vdw_tail   = demoline[1]
#                     vdw_func   = int(demoline[2])
#                     vdw_c6     = float(demoline[3])
#                     vdw_c12    = float(demoline[4])
#                     itpVdwPair_list.append (ItpVdwPair(vdw_head, vdw_tail, vdw_func, vdw_c6, vdw_c12))
#                     #print(vdw_head, vdw_tail, vdw_func, vdw_c6, vdw_c12) # test ok
#     return itpVdwPair_list
