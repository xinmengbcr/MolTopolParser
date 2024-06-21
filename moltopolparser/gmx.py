"""
This module contains the classes and functions to parse Gromacs files.
"""

import os
from typing import List, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

import re

# -----------< Base >----------- #


class GroAtom(BaseModel):
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


class MolForceFieldDefaults(BaseModel):
    """section [ defaults ] in the itp file
    example:
    --------
    ; nbfunc        comb-rule       gen-pairs       fudgeLJ fudgeQQ
    1               2               yes             0.5     0.8333
    --------
    """

    nbfunc: int = Field(..., description="Number of functions")
    comb_rule: int = Field(..., description="Combination rule")
    gen_pairs: Optional[str] = Field(None, description="Generate pairs")
    fudgeLJ: Optional[float] = Field(None, description="Fudge LJ")
    fudgeQQ: Optional[float] = Field(None, description="Fudge QQ")

    @classmethod
    def title(cls) -> str:
        return "defaults"

    @classmethod
    def parser(cls, content: List[str]) -> "MolForceFieldDefaults":
        """
        Parse the full content of the section [ defaults ].
        """
        start, _, _, _ = find_section_range(content, cls.title())
        if start == -1:
            raise ValueError(f"Section [ {cls.title()} ] not found in the content.")

        target_line = content[start + 1].strip()
        parts = target_line.split()

        data = {
            "nbfunc": int(parts[0]),
            "comb_rule": int(parts[1]),
            "gen_pairs": parts[2] if len(parts) > 2 else None,
            "fudgeLJ": float(parts[3]) if len(parts) > 3 else None,
            "fudgeQQ": float(parts[4]) if len(parts) > 4 else None,
        }

        return cls(**data)


class MolForceFieldAtomtype(BaseModel):
    """
    Represents an atom type in a force field.
    example for AA (amber):
    --------
    [ atomtypes ]
    ;name     at.num    mass     charge    ptype  sigma        epsilon
    C            6      12.01    0.0000    A      3.39967e-01  3.59824e-01
    --------
    example for CG (Martini):
    [ atomtypes ]
    ;name   mass     charge    ptype  sigma      epsilon
    P5      72.0     0.000      A     0.0         0.0
    --------
    """

    name: str = Field(..., description="Atom type")
    at_num: Optional[int] = Field(None, description="Atomic number")
    mass: float = Field(..., description="Atom mass")
    charge: float = Field(..., description="Charge")
    ptype: str = Field(..., description="Particle type")
    sigma: float = Field(..., description="Sigma")
    epsilon: float = Field(..., description="Epsilon")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "name": "C",
                "at_num": 6,
                "mass": 12.01,
                "charge": 0.0000,
                "ptype": "A",
                "sigma": 3.39967e-01,
                "epsilon": 3.59824e-01,
            },
              {
                "name": "P5",
                "mass": 72.0,
                "charge": 0.000,
                "ptype": "A",
                "sigma": 0.0,
                "epsilon": 0.0,
            }]
        },
    )

    @classmethod
    def title(cls) -> str:
        return "atomtypes"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolForceFieldAtomtype"]:
        """
        Parse the full content of the section [ atomtypes ].
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )
        if start == -1:
            raise ValueError(f"Section [ {cls.title()} ] not found in the content.")
        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                parts = target_line.split()[:7]  # maxumum 7 parts
                # remove the last element if starts with ;
                if parts[-1].startswith(";"):
                    parts = parts[:-1]
                # check it is cg or aa
                if len(parts) == 7:
                    data = {
                        "name": parts[0],
                        "at_num": int(parts[1]),
                        "mass": float(parts[2]),
                        "charge": float(parts[3]),
                        "ptype": parts[4],
                        "sigma": float(parts[5]),
                        "epsilon": float(parts[6]),
                    }
                elif len(parts) == 6:
                    data = {
                        "name": parts[0],
                        "mass": float(parts[1]),
                        "charge": float(parts[2]),
                        "ptype": parts[3],
                        "sigma": float(parts[4]),
                        "epsilon": float(parts[5]),
                    }
                else:
                    raise ValueError("The atomtype line is not formatted correctly.")
                instance_list.append(cls(**data))
        return instance_list


class MolForceFieldNonbondParam(BaseModel):
    """section [ nonbond_params ] in the itp file
    example for CG (martini):
    --------
    [ nonbond_params ]
     P5    P5      1       0.24145E-00     0.26027E-02 ; supra attractive
    --------
    Note:
    - only Martini 2.2 is tested.
    """

    ai: str = Field(..., description="First atom index")
    aj: str = Field(..., description="Second atom index")
    func: int = Field(..., description="Function type")
    c6: float = Field(..., description="C6")
    c12: float = Field(..., description="C12")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": "P5",
                "aj": "P5",
                "func": 1,
                "c6": 0.24145e-00,
                "c12": 0.26027e-02,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "nonbond_params"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolForceFieldNonbondParam"]:
        """
        Parse the full content of the section [ nonbond_params ].
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )

        if start == -1:
            print(f"warning: not section {cls.title()} is found")
            return None

        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                parts = target_line.split()[:5]  # maxumum 5 parts
                data = {
                    "ai": parts[0],
                    "aj": parts[1],
                    "func": int(parts[2]),
                    "c6": float(parts[3]),
                    "c12": float(parts[4]),
                }
                instance_list.append(cls(**data))
        return instance_list


class MolForceFieldBondtype(BaseModel):
    """
    section [ bondtypes ] in the itp file
    example AA (amber):
    --------
    [ bondtypes ]
    ; i    j  func       b0          kb
    C  C          1     0.1525   259408.0 ; new99
    --------
    Note:
    - only AmberFF is tested.
    """

    ai: str = Field(..., description="First atom type")
    aj: str = Field(..., description="Second atom type")
    func: int = Field(..., description="Function type")
    b0: float = Field(..., description="Equilibrium bond length")
    kb: float = Field(..., description="Bond force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": "C",
                "aj": "C",
                "func": 1,
                "b0": 0.1525,
                "kb": 259408.0,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "bondtypes"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolForceFieldBondtype"]:
        """
        Parse the full content of the section [ bondtypes ].
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                parts = target_line.split()[:5]  # maxumum 5 parts
                data = {
                    "ai": parts[0],
                    "aj": parts[1],
                    "func": int(parts[2]),
                    "b0": float(parts[3]),
                    "kb": float(parts[4]),
                }
                instance_list.append(cls(**data))
        return instance_list


class MolForceFieldAngletype(BaseModel):
    """
    section [ angletypes ] in the itp file
    example AA (amber):
    --------
    [ angletypes ]
    ;  i    j    k  func       th0       cth
    HW  OW  HW           1   104.520    836.800 ; TIP3P water
    --------
    """

    ai: str = Field(..., description="First atom type")
    aj: str = Field(..., description="Second atom type")
    ak: str = Field(..., description="Third atom type")
    func: int = Field(..., description="Function type")
    th0: float = Field(..., description="Equilibrium angle")
    cth: float = Field(..., description="Angle force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": "HW",
                "aj": "OW",
                "ak": "HW",
                "func": 1,
                "th0": 104.520,
                "cth": 836.800,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "angletypes"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolForceFieldAngletype"]:
        """
        Parse the full content of the section [ angletypes ].
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                parts = target_line.split()[:6]  # maxumum 6 parts
                data = {
                    "ai": parts[0],
                    "aj": parts[1],
                    "ak": parts[2],
                    "func": int(parts[3]),
                    "th0": float(parts[4]),
                    "cth": float(parts[5]),
                }
                instance_list.append(cls(**data))
        return instance_list


class MolForceFieldDihedraltype(BaseModel):
    """
    Base class for dihedral in a force field,
    defined in section [ dihedrals ] in the itp file
    example amber , func=4:
    --------
    [ dihedraltypes ]
    ;i  j   k  l     func      phase      kd      pn
    CA  CA  CA  OH       4      180.00     4.60240     2    ; new99
    --------
    example amber, func=9:
    --------
    [ dihedraltypes ]
    ;i   j   k   l     func
    CT  CT  OS  CT    9       0.0      1.60247     3  ;
    --------
    example opls, func=3:
    --------
    [ dihedraltypes ]
    ;  i    j    k    l   func     coefficients
    Br     C      CB     CT      3      0.00000   0.00000   0.00000   0.00000   0.00000   0.00000 ; acyl halide
    --------

    Note on the function type:
    - When function type is 3 or 5, all coefficients c0 to c5 are required.
    - When function type is 4 or 9, c0, c1 are required as float, c2 is required as integer, and c3 to c5 are optional.
    - Other function type validations are not implemented.
    """  # noqa: E501

    ai: str = Field(..., description="First atom index")
    aj: str = Field(..., description="Second atom index")
    ak: str = Field(..., description="Third atom index")
    al: str = Field(..., description="Fourth atom index")
    func: int = Field(..., description="Dihedral function")
    c0: float = Field(None, description="c0")
    c1: float = Field(None, description="c1")
    c2: Union[float, int] = Field(None, description="c2")
    c3: Optional[float] = Field(None, description="c3")
    c4: Optional[float] = Field(None, description="c4")
    c5: Optional[float] = Field(None, description="c5")

    @model_validator(mode="before")
    def check_func_and_coefficients(cls, values):
        func = values.get("func")
        if func in (3, 5):
            for field in ["c0", "c1", "c2", "c3", "c4", "c5"]:
                if values.get(field) is None:
                    raise ValueError(f"{field} is required when func is {func}.")
        elif func in (4, 9):
            if values.get("c0") is None or values.get("c1") is None:
                raise ValueError("c0 and c1 are required when func is 4 or 9.")
            if values.get("c2") is None:
                raise ValueError("c2 is required when func is 4 or 9.")
            if not isinstance(values.get("c2"), int):
                raise ValueError("c2 must be an integer when func is 4 or 9.")
        else:
            raise ValueError("Only func values 3, 4, 5, and 9 are supported.")

        if func not in (3, 5):
            for field in ["c3", "c4", "c5"]:
                if values.get(field) is not None:
                    raise ValueError(
                        f"{field} can only have a value if func is 3 or 5."
                    )
        return values

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ai": "CA",
                    "aj": "CA",
                    "ak": "CA",
                    "al": "OH",
                    "func": 4,
                    "c0": 180.00,
                    "c1": 4.60240,
                    "c2": 2,
                    # c3 to c5 are optional
                },
                {
                    "ai": "Br",
                    "aj": "C",
                    "ak": "CB",
                    "al": "CT",
                    "func": 3,
                    "c0": 0.00000,
                    "c1": 0.00000,
                    "c2": 0.00000,
                    "c3": 0.00000,
                    "c4": 0.00000,
                    "c5": 0.00000,
                },
            ]
        }
    )

    @classmethod
    def title(cls) -> str:
        return "dihedraltypes"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolForceFieldDihedraltype"]:
        """
        Parse the full content of the section
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                target_line = filter_comment(target_line)  # clean ;
                # the length of the line split should be 8 or 11
                if len(target_line.split()) == 8:
                    parts = target_line.split()[:8]
                    data = {
                        "ai": parts[0],
                        "aj": parts[1],
                        "ak": parts[2],
                        "al": parts[3],
                        "func": int(parts[4]),
                        "c0": float(parts[5]),
                        "c1": float(parts[6]),
                        "c2": int(parts[7]),
                        "c3": None,
                        "c4": None,
                        "c5": None,
                    }
                elif len(target_line.split()) == 11:
                    parts = target_line.split()[:11]
                    data = {
                        "ai": parts[0],
                        "aj": parts[1],
                        "ak": parts[2],
                        "al": parts[3],
                        "func": int(parts[4]),
                        "c0": float(parts[5]),
                        "c1": float(parts[6]),
                        "c2": int(parts[7]),
                        "c3": float(parts[8]),
                        "c4": float(parts[9]),
                        "c5": float(parts[10]),
                    }
                else:
                    raise ValueError(
                        "The dihedraltype line is not formatted correctly."
                    )
                instance_list.append(cls(**data))
        return instance_list


class MolTopHeader(BaseModel):
    """
    Represents the header of the [ moleculetype ] section in a molecule topology.
    """

    name: str = Field(..., description="Molecule name")
    nrexcl: int = Field(..., description="Number of exclusions")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "SOL",
                "nrexcl": 3,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "moleculetype"

    @classmethod
    def parser(cls, content: List[str]) -> "MolTopHeader":
        """
        Parse section [ moleculetype ].
        """
        start, _, _, _ = find_section_range(content, cls.title())
        if start == -1:
            raise ValueError(f"Section [ {cls.title()} ] not found")

        target_line = content[start + 1].strip()
        parts = target_line.split()

        data = {
            "name": parts[0],
            "nrexcl": int(parts[1]),
        }

        return cls(**data)


class MolTopAtom(BaseModel):
    """
    Base class for atom in a molecule topology, defined in [ atoms ] section
    """

    id: int = Field(..., description="Atom index")
    atom_type: str = Field(..., description="Atom type")
    resnr: int = Field(..., description="Residue number")
    residu: str = Field(..., description="Residue name")
    atom: str = Field(..., description="Atom name")
    cgnr: int = Field(..., description="Charge group number")
    charge: float = Field(..., description="Charge")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "atom_type": "C",
                "resnr": 1,
                "residu": "UREA",
                "atom": "C1",
                "cgnr": 1,
                "charge": 0.683,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "atoms"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolTopAtom"]:
        """
        Parse the full content of the section [ atoms ].
        """
        instance_list = []
        start, end, _, _ = find_section_range(content, cls.title())

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # in one molecule type, such a section is single
        data_target = content[start + 1 : end]  # +1 to skip [] line
        for target_line in data_target:
            target_line = filter_comment(target_line)  # clean ;
            parts = target_line.split()[:7]
            data = {
                "id": int(parts[0]),
                "atom_type": parts[1],
                "resnr": int(parts[2]),
                "residu": parts[3],
                "atom": parts[4],
                "cgnr": int(parts[5]),
                "charge": float(parts[6]),
            }
            instance_list.append(cls(**data))

        return instance_list


class MolTopBond(BaseModel):
    """
    Base class for bond in a molecule topology, defined in [ bonds ] section
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    func: Optional[int] = Field(1, description="Bond function")
    c0: Optional[float] = Field(None, description="Equilibrium bond length")
    c1: Optional[float] = Field(None, description="Bond force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ai": 1,
                    "aj": 2,
                    "func": 1,
                    "c0": 1.0,
                    "c1": 100.0,
                },
                {
                    "ai": 1,
                    "aj": 2,
                    "func": 1,
                },
                {
                    "ai": 1,
                    "aj": 2,
                },
            ]
        },
    )

    @classmethod
    def title(cls) -> str:
        return "bonds"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolTopBond"]:
        """
        Parse the full content of the section [ bonds ].
        """
        instance_list = []
        start, end, _, _ = find_section_range(content, cls.title())

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # in one molecule type, such a section is single
        data_target = content[start + 1 : end]  # +1 to skip [] line
        data = None
        for target_line in data_target:
            target_line = filter_comment(target_line)  # clean ;
            parts = target_line.split()
            if len(parts) == 5:
                data = {
                    "ai": int(parts[0]),
                    "aj": int(parts[1]),
                    "func": int(parts[2]),
                    "c0": float(parts[3]),
                    "c1": float(parts[4]),
                }
            elif len(parts) == 3 or len(parts) == 4:
                # print("Warning: c0 and c1 are not provided")
                data = {
                    "ai": int(parts[0]),
                    "aj": int(parts[1]),
                    "func": int(parts[2]),
                    "c0": None,
                    "c1": None,
                }
            elif len(parts) == 2:
                # print("Warning: func and c0, c1 are not provided")
                data = {
                    "ai": int(parts[0]),
                    "aj": int(parts[1]),
                }
            else:
                raise ValueError("The bond line is not formatted correctly.")

            if data is not None:
                instance_list.append(cls(**data))
                return instance_list
            else:
                return None


class MolTopPair(BaseModel):
    """
    Base class for pair in a molecule topology, defined in [ pairs ] section
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": 1,
                "aj": 2,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "pairs"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolTopPair"]:
        """
        Parse the full content of the section [ pairs ].
        """
        instance_list = []
        start, end, _, _ = find_section_range(content, cls.title())

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # in one molecule type, such a section is single
        data_target = content[start + 1 : end]
        for target_line in data_target:
            target_line = filter_comment(target_line)
            parts = target_line.split()
            data = {
                "ai": int(parts[0]),
                "aj": int(parts[1]),
            }
            instance_list.append(cls(**data))

        return instance_list


class MolTopAngle(BaseModel):
    """
    Base class for angle in a molecule topology defined in [ angles ] section
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    ak: int = Field(..., description="Third atom index")
    func: int = Field(..., description="Angle function")
    c0: Optional[float] = Field(None, description="Equilibrium angle")
    c1: Optional[float] = Field(None, description="Angle force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": 1,
                "aj": 2,
                "ak": 3,
                "func": 1,
                "c0": 180.0,
                "c1": 100.0,
            }
        }
    )

    @classmethod
    def title(cls) -> str:
        return "angles"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolTopAngle"]:
        """
        Parse the full content of the section [ angles ].
        """
        instance_list = []
        start, end, _, _ = find_section_range(content, cls.title())

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # in one molecule type, such a section is single
        data_target = content[start + 1 : end]
        for target_line in data_target:
            target_line = filter_comment(target_line)
            parts = target_line.split()
            if len(parts) == 6:
                data = {
                    "ai": int(parts[0]),
                    "aj": int(parts[1]),
                    "ak": int(parts[2]),
                    "func": int(parts[3]),
                    "c0": float(parts[4]),
                    "c1": float(parts[5]),
                }
            else:
                # print("Warning: c0 and c1 are not provided")
                data = {
                    "ai": int(parts[0]),
                    "aj": int(parts[1]),
                    "ak": int(parts[2]),
                    "func": int(parts[3]),
                    "c0": None,
                    "c1": None,
                }

            instance_list.append(cls(**data))
        return instance_list


class MolTopDihedral(BaseModel):
    """
    Base class for dihedral in a molecule topology,
    defined in [ dihedrals ] section

    Note on the function type:
    - Validation: only when func is 3 or 5, c3 to c5 can be supplied
    - Other function type validations are not implemented.
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    ak: int = Field(..., description="Third atom index")
    al: int = Field(..., description="Fourth atom index")
    func: int = Field(..., description="Dihedral function")
    c0: Optional[float] = Field(None, description="c0")
    c1: Optional[float] = Field(None, description="c1")
    c2: Optional[float] = Field(None, description="c2")
    c3: Optional[float] = Field(None, description="c3")
    c4: Optional[float] = Field(None, description="c4")
    c5: Optional[float] = Field(None, description="c5")

    @model_validator(mode="before")
    def check_func_and_coefficients(cls, values):
        func = values.get("func")
        if func not in (3, 5):
            for field in ["c3", "c4", "c5"]:
                if values.get(field) is not None:
                    raise ValueError(
                        f"{field} can only have a value if func is 3 or 5."
                    )
        return values

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": 1,
                "aj": 2,
                "ak": 3,
                "al": 4,
                "func": 3,
                "c0": 0.0,
                "c1": 1.0,
                "c2": 2.0,
                "c3": 3.0,
                "c4": 4.0,
                "c5": 5.0,
            },
        }
    )

    @classmethod
    def title(cls) -> str:
        return "dihedrals"

    @classmethod
    def parser(cls, content: List[str]) -> List["MolTopDihedral"]:
        """
        Parse the full content of the section [ dihedrals ].
        """
        instance_list = []
        start, end, idx_section, idx_section_general = find_section_range(
            content, cls.title()
        )

        if start == -1:
            # print(f"warning: not section {cls.title()} is found")
            return None

        # in one molecule type, such a section can be defined multiple times
        # for reasoning like split dihedrals by their function type
        for idx in idx_section:
            start = idx
            try:
                end = idx_section_general[idx_section_general.index(start) + 1]
                data_target = content[start + 1 : end]
            except IndexError:
                end = False
                data_target = content[start + 1 :]  # Not data[start:-1]

            for target_line in data_target:
                target_line = filter_comment(target_line)
                parts = target_line.split()
                if len(parts) == 8:
                    data = {
                        "ai": int(parts[0]),
                        "aj": int(parts[1]),
                        "ak": int(parts[2]),
                        "al": int(parts[3]),
                        "func": int(parts[4]),
                        "c0": float(parts[5]),
                        "c1": float(parts[6]),
                        "c2": float(parts[7]),
                        "c3": None,
                        "c4": None,
                        "c5": None,
                    }
                elif len(parts) == 11:
                    data = {
                        "ai": int(parts[0]),
                        "aj": int(parts[1]),
                        "ak": int(parts[2]),
                        "al": int(parts[3]),
                        "func": int(parts[4]),
                        "c0": float(parts[5]),
                        "c1": float(parts[6]),
                        "c2": float(parts[7]),
                        "c3": float(parts[8]),
                        "c4": float(parts[9]),
                        "c5": float(parts[10]),
                    }
                else:
                    # print("Warning: c0 to c5 are not provided")
                    data = {
                        "ai": int(parts[0]),
                        "aj": int(parts[1]),
                        "ak": int(parts[2]),
                        "al": int(parts[3]),
                        "func": int(parts[4]),
                        "c0": None,
                        "c1": None,
                        "c2": None,
                        "c3": None,
                        "c4": None,
                        "c5": None,
                    }

                instance_list.append(cls(**data))
        return instance_list


# ----------< Aggregation Data >---------- #


class MolForceField(BaseModel):
    """
    Represents a molecular force field.
    Note:
    - all the sections exept [ defaults ] can have multiple entries.
    """

    defaults: MolForceFieldDefaults = Field(
        ..., description="Force field defaults setup"
    )
    atomtypes: List[MolForceFieldAtomtype] = Field(..., description="Atomtypes")
    nonbond_params: Optional[List[MolForceFieldNonbondParam]] = Field(
        ..., description="Nonbond parameters"
    )
    bondtypes: Optional[List[MolForceFieldBondtype]] = Field(
        ..., description="Bond types"
    )
    angletypes: Optional[List[MolForceFieldAngletype]] = Field(
        ..., description="Angle types"
    )
    dihedraltypes: Optional[List[MolForceFieldDihedraltype]] = Field(
        ..., description="Dihedral types"
    )

    @classmethod
    def parser(
        cls,
        content_lines: Optional[List[str]] = None,
        content_files: Optional[List[str]] = None,
    ):
        """
        Parse the force field parameters from the content_lines or content_files.
        """
        # contains the whole content of the force field
        ff_content = clean_lines(content_lines, content_files)
        # prepare attibutes
        defaults = MolForceFieldDefaults.parser(ff_content)
        atomtypes = MolForceFieldAtomtype.parser(ff_content)
        nonbond_params = MolForceFieldNonbondParam.parser(ff_content)
        bondtypes = MolForceFieldBondtype.parser(ff_content)
        angletypes = MolForceFieldAngletype.parser(ff_content)
        dihedraltypes = MolForceFieldDihedraltype.parser(ff_content)

        data = {
            "defaults": defaults,
            "atomtypes": atomtypes,
            "nonbond_params": nonbond_params,
            "bondtypes": bondtypes,
            "angletypes": angletypes,
            "dihedraltypes": dihedraltypes,
        }
        return MolForceField(**data)


class MolTop(BaseModel):
    """[ moleculetype ] section .
    example data posted at link:
    /docs/data_reference/gmx_molecule_topology.md
    """

    # molecule_type is a dictionary with the molecule name and nrexcl
    header: MolTopHeader = Field(..., description="Molecule name and nrexcl")
    atoms: List[MolTopAtom] = Field(..., description="Atoms in molecule")
    bonds: Optional[List[MolTopBond]] = Field(..., description="Bonds in molecule")
    pairs: Optional[List[MolTopPair]] = Field(..., description="Pairs in molecule")
    angles: Optional[List[MolTopAngle]] = Field(..., description="Angles in molecule")
    dihedrals: Optional[List[MolTopDihedral]] = Field(
        ..., description="Dihedrals in molecule"
    )

    @classmethod
    def parser(
        cls,
        content_lines: Optional[List[str]] = None,
        content_files: Optional[List[str]] = None,
        molecule_types: Optional[List[str]] = None,
    ):
        """
        Parse the molecule topology from the content_lines or content_files.
        Different with the force field, the molecule topology can have multiple entries.
        Since the loop is skipped from the summerization level, thus it is done here.
        """
        # instances of the molecule topology
        instance_list = []

        # contains the whole content of the molecule topology
        mt_content = clean_lines(content_lines, content_files)
        # find the sectioln [ moleculetype ]
        start, end, idx_section, idx_section_general = find_section_range(
            mt_content, "moleculetype"
        )
        if start == -1:
            # print(f"warning: not section moleculetype is found")
            return None

        # the moleculetype section is the same level as the other sections
        # like atoms, bonds, etc.
        # Here has to extract the whole content of the molecule type
        # so that the other sections can be parsed.
        # the machtching section can be multiple times in the content
        # so we need to loop over idx_section lists
        # the end should be the next moleculetype or the end lines of the content
        for idx in idx_section:
            start = idx
            try:
                end = idx_section[idx_section.index(start) + 1]
                mt_section = mt_content[
                    start:end
                ]  # note this one contains the [ moleculetype ]
            except IndexError:
                end = False
                mt_section = mt_content[start:]

            # normal parsing of the molecule type
            header = MolTopHeader.parser(mt_section)
            atoms = MolTopAtom.parser(mt_section)
            bonds = MolTopBond.parser(mt_section)
            angles = MolTopAngle.parser(mt_section)
            pairs = MolTopPair.parser(mt_section)
            dihedrals = MolTopDihedral.parser(mt_section)

            data = {
                "header": header,
                "atoms": atoms,
                "bonds": bonds,
                "pairs": pairs,
                "angles": angles,
                "dihedrals": dihedrals,
            }

            instance_list.append(MolTop(**data))
        return instance_list


# ----------< Aggregation Data >---------- #

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
    gro_atoms: List[GroAtom] = Field(..., description="List of atoms")
    box_size: List[float] = Field(..., description="Box size")

    @classmethod
    def parser(cls, file: str):
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
        with open(file, encoding="utf-8") as f:
            lines = f.readlines()
            num_atoms = int(lines[1])
            box_size = np.array(
                lines[_skip_lines + num_atoms].strip("\n").lstrip().split(), dtype=float
            )
        gro_atoms: List[GroAtom] = []
        for line in lines[_skip_lines: _skip_lines + num_atoms]:
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
            gro_atoms.append(GroAtom(**atom_data))
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

# ----------< Summarization Data >---------- #


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
    molecules: List[dict[str, int]] = Field(..., description="Molecules and counts")
    include_itps: Optional[List[str]] = Field(None, description="Include files")
    molecule_topologies: Optional[List[MolTop]] = Field(
        None, description="Topologies defined in the top file"
    )
    forcefield: Optional[MolForceField] = Field(None, description="Force field")
    inlines: Optional[List[str]] = Field(
        None,
        description="directly given in .top file that can \
        be any content in force field or molecule topology",
    )

    @property
    def moleculetypes(self):
        """
        Return the molecule types from the molecules section with no duplicates.
        """
        molecule_set = {list(mol.keys())[0] for mol in self.molecules}
        return list(molecule_set)

    def pull_forcefield(self):
        """
        Pull the force field parameters from the inlines and include_itps
        """
        inlines = self.inlines or []
        include_itps = self.include_itps or []
        if self.forcefield is None:
            self.forcefield = MolForceField.parser(inlines, include_itps)
        else:
            raise ValueError("Force field already exists in the topology.")
        # return self.forcefield

    def pull_molecule_topologies(self):
        """
        Pull the molecule topologies from the inlines and include_itps
        """
        inlines = self.inlines or []
        include_itps = self.include_itps or []
        if self.molecule_topologies is None:
            self.molecule_topologies = []
            # search for the molecule_topology included in the systems
            # if self.moleculetypes is not supplied; then all the molecule types
            # avaliable are included
            self.molecule_topologies = MolTop.parser(
                inlines, include_itps, self.moleculetypes
            )
        else:
            raise ValueError("Molecule topologies already exist in the topology.")
        return self.molecule_topologies
        
    @classmethod
    def parser(cls, filename: str):
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
        system_molecules = []
        itp_paths = []
        with open(filename, "r", encoding="utf-8") as infile:
            lines = infile.readlines()
            # clean data; throw the lines that start with ; or empty lines
            lines = [
                line.strip() for line in lines if not line.startswith(";") and line.strip()
            ]
            # deepcopy of the lines
            inlines = lines.copy()

            # look for the section [ system ]
            start, _, _, _ = find_section_range(lines, "system")
            system_name = lines[start + 1]
            inlines.remove(lines[start])
            inlines.remove(lines[start + 1])

            # look for the section [ molecules ]
            start, end, _, _ = find_section_range(lines, "molecules")
            data_target = lines[start + 1: end] if end else lines[start + 1:]
            for line in data_target:
                molname, molnum = line.split()[:2]
                system_molecules.append({molname: int(molnum)})

            # remove the lines inside the data_target and the header line
            for line in data_target:
                inlines.remove(line)
            inlines.remove(lines[start])

            # look for the included files, lines starting with #
            target_lines = [line for line in lines if line.startswith("#include")]
            if target_lines:
                for line in target_lines:
                    # get rid of the inline comments that starts with ;
                    line_wo_comment = line.split(";")[0]
                    path = line_wo_comment.split()[1]
                    if path is not None:
                        itp_paths.append(
                            f"{os.path.dirname(os.path.abspath(filename))}/{path[1:-1]}"
                        )  # strip sorrounding quotes
                    # remove the lines inside the target_lines
                    inlines.remove(line)
            else:
                itp_paths = None

            # second layer of #include files
            # this helps to get the ffnonbonded.itp or ffbonded.itp
            # inside a forcefield.itp
            for itp_path in itp_paths.copy():
                with open(itp_path, "r", encoding="utf-8") as itpfile:
                    itplines = itpfile.readlines()
                    itplines = [
                        line.strip() for line in itplines if not line.startswith(";")
                    ]
                    target_lines = [
                        line for line in itplines if line.startswith("#include")
                    ]
                    if target_lines:
                        for line in target_lines:
                            # get rid of the inline comments that starts with ;
                            line_wo_comment = line.split(";")[0]
                            path = line_wo_comment.split()[1]
                            if path is not None:
                                itp_paths.append(
                                    f"{os.path.dirname(os.path.abspath(itp_path))}/{path[1:-1]}"
                                )  # strip sorrounding quotes

            if not inlines:
                inlines = None

            # sum up the data
            top_data = {
                "system": system_name,
                "molecules": system_molecules,
                "include_itps": itp_paths,
                "inlines": inlines,
            }
            return Topology(**top_data)



# ----------< Helper function >---------- #


def find_section_range(lines: List[str], section_name: str) -> tuple[int, int]:
    """
    Find the range of a section in the lines.
    """
    pattern = re.compile(rf"\[\s*{re.escape(section_name)}\s*\]", re.IGNORECASE)

    idx_section = [x for x in range(len(lines)) if pattern.search(lines[x])]

    # idx_section_general = [
    #     x for x in range(len(lines)) if ("[ " in lines[x].lower())
    # ]
    idx_section_general = [
        x for x in range(len(lines)) if re.search(r"\[\s*\w+\s*\]", lines[x].lower())
    ]

    try:
        start = idx_section[0]  # section [ section_name ]
    except IndexError:
        start = -1
        return start, -1, idx_section, idx_section_general

    try:
        next_index = idx_section_general.index(start) + 1
        end = idx_section_general[next_index]  # next '[' idx
    except IndexError:
        end = len(lines)

    return start, end, idx_section, idx_section_general


def clean_lines(
    lines: Optional[List[str]] = None, files: Optional[List[str]] = None
) -> List[str]:
    """
    read lines or files and
    filter out emtpy lines and lines starting *comment_start_sysmbols*
    and remove space and \n
    - via inlcude the "#", the #define and #ifdef are also removed
    """
    content = []
    comment_start_sysmbols = (";", "*", "#include", "#")
    if lines is not None and lines != []:
        lines = [
            line.strip()
            for line in lines
            if line.strip() and not line.startswith(comment_start_sysmbols)
        ]
        content.extend(lines)
    if files is not None and files != []:
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                lines = [
                    line.strip()
                    for line in f.readlines()
                    if line.strip() and not line.startswith(comment_start_sysmbols)
                ]
                content.extend(lines)
    return content


def filter_comment(line: str) -> str:
    """
    Filter out the content of the line after the ';' character.

    Parameters:
    line (str): The line of data.

    Returns:
    str: The line with the content after ';' removed.
    """
    # Split the line at the first occurrence of ';' and return the first part
    return line.split(";")[0].strip()


if __name__ == "__main__":
    print("run gmx directly")
    input_file = "../tests/data/gmx/twolayer_include_itp/system.top"
    sys_top = Topology.parser(input_file)
    demo, demo2 = sys_top.pull_forcefield()
