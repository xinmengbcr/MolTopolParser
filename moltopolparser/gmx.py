"""
This module contains the classes and functions to parse Gromacs files.

"""
import numpy as np
from pydantic import BaseModel, Field, ConfigDict


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
    groatoms: list of GroFileAtom
    box_size: np.array
    """

    sys_name: str = Field(..., description="System name")
    num_atoms: int = Field(..., description="Number of atoms")
    gro_atoms: list[GroFileAtom] = Field(..., description="List of atoms")
    box_size: list[float] = Field(..., description="Box size")



def parse_gro_file(input_file):
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
            lines[_skip_lines + num_atoms].strip("\n")
            .lstrip().split(), dtype=float
        )
    gro_atoms = []
    for line in lines[_skip_lines:_skip_lines + num_atoms]:
        line_length = len(line)
        atom_data = {
            "resid": int(line[:5]),
            "resname": line[5:10].strip(),
            "atom_name":line[10:15].strip(),
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
                "The line lenght is {line_length} "
                "while it should be 45 for a gro file containing positions only "
                "or 69 for a gro file containing both positions and velocities."
            )
    return GroFile(
        sys_name=lines[0].strip("\n"),
        num_atoms=num_atoms,
        gro_atoms=gro_atoms,
        box_size=box_size,
    )
