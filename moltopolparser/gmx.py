"""
This module contains the classes and functions to parse Gromacs files.
"""

import os
from typing import List, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator


# -----------< Base Data >----------- #


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
    gen_pairs: Optional[str] = Field(..., description="Generate pairs")
    fudgeLJ: Optional[float] = Field(..., description="Fudge LJ")
    fudgeQQ: Optional[float] = Field(..., description="Fudge QQ")


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
    at_num: Optional[int] = Field(..., description="Atomic number")
    mass: float = Field(..., description="Atom mass")
    charge: float = Field(..., description="Charge")
    ptype: Optional[str] = Field(..., description="Particle type")
    sigma: float = Field(..., description="Sigma")
    epsilon: float = Field(..., description="Epsilon")


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
    k: str = Field(..., description="Third atom type")
    func: int = Field(..., description="Function type")
    th0: float = Field(..., description="Equilibrium angle")
    cth: float = Field(..., description="Angle force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": "HW",
                "aj": "OW",
                "k": "HW",
                "func": 1,
                "th0": 104.520,
                "cth": 836.800,
            }
        }
    )


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


class MolTopBond(BaseModel):
    """
    Base class for bond in a molecule topology, defined in [ bonds ] section
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    func: int = Field(..., description="Bond function")
    c0: float = Field(..., description="Equilibrium bond length")
    c1: float = Field(..., description="Bond force constant")
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ai": 1,
                "aj": 2,
                "func": 1,
                "c0": 1.0,
                "c1": 100.0,
            }
        }
    )


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


class MolTopAngle(BaseModel):
    """
    Base class for angle in a molecule topology defined in [ angles ] section
    """

    ai: int = Field(..., description="First atom index")
    aj: int = Field(..., description="Second atom index")
    ak: int = Field(..., description="Third atom index")
    func: int = Field(..., description="Angle function")
    c0: float = Field(..., description="Equilibrium angle")
    c1: float = Field(..., description="Angle force constant")
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


# ----------< Aggregation Data >---------- #


class MolForceField(BaseModel):
    """
    Represents a force field in a molecule topology.
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
    # dihedraltypes: Optional[List[MolForceFieldDihedraltypes]] = Field(
    #     ..., description="Dihedral types")

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
        ff_content = []
        # check attributes
        if not content_lines and not content_files:
            raise ValueError("Either content_lines or content_files must be provided.")
        # sum up the content
        if content_lines not in (None, []):
            ff_content.extend(content_lines)
        if content_files not in (None, []):
            # read lines from the files
            for file in content_files:
                with open(file, "r", encoding="utf-8") as f:
                    # clean the lines 
                    lines = [line.strip() for line in f.readlines() if not line.startswith(";")]
                    ff_content.extend(lines)
        #print(ff_content)
        return ff_content

        
        


class MolTop(BaseModel):
    """[ moleculetype ] section .
    example data posted at link:
    https://github.com/xinmengbcr/MolTopolParser/wiki/Data-Format-%E2%80%90-GMX-%E2%80%90-Molecule-Topology-Definition
    """

    # molecule_type is a dictionary with the molecule name and nrexcl
    molecule_type: dict[str, int] = Field(..., description="Molecule type")
    atoms: List[MolTopAtom] = Field(..., description="Atoms in molecule")
    bonds: List[MolTopBond] = Field(..., description="Bonds in molecule")
    pairs: Optional[List[MolTopPair]] = Field(..., description="Pairs in molecule")
    angles: Optional[List[MolTopAngle]] = Field(..., description="Angles in molecule")
    dihedrals: Optional[List[MolTopDihedral]] = Field(
        ..., description="Dihedrals in molecule"
    )


# ----------< Aggregation-File Data >---------- #


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

    # TBD: Add dump method to write the gro file, or convert to other formats


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

    # sort out the force field parameters
    def pull_forcefield(self):
        """
        Pull the force field parameters from the inlines and include_itps
        """
        inlines = self.inlines or []
        include_itps = self.include_itps or []
        # self.forcefield = MolForceField.paser(inlines, include_itps)
        demo = MolForceField.parser(inlines, include_itps)
        return demo

    # --- TBD: sort out molecular topologies/force field parameters.
    # one ways is to do it here in the class:
    # loop set(molecule types/names) --> parse the inlines and include_itps
    # --> filling the MolTop --> add in the molecule_topologies
    # molecule_types = sort_molecule_types(self.molecules)
    # call class method MolTop
    # sort_out_molecule_topologies(molecule_types, self.inlines, self.include_itps)
    # so the parser should happen in their corresponding data levels.
    # Summerization level entry of the whole system/content
    # The Summerization level level, calls and organises aggregation level.
    # The aggregation/ aggregation-file level handles the real parsing
    # The base data level. just uses the direct data definiation
    #
    # so the parser functions can go as the class methods in the aggregation level?
    # and the summerization level can call the aggregation level methods to parse the data
    # and organise the data in the big picture.
    #
    # then the aggregation level works like a componennt in React.
    # the summarnization level works like the main component that calls the sub-components.
    # and able to pass the data
    #
    # Of course, the aggregation level can also have to dump methods to convert or write out the data
    # Then this is anther call after the parsing, when we already organised the aggregation data.
    #


# ----------< File Parser Function >---------- #


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
    gro_atoms: List[GroAtom] = []
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


def parse_top_file(filename: str) -> tuple[dict[str, int], list[str]]:
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
        data_target = lines[start + 1 : end] if end else lines[start + 1 :]
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
    idx_section = [
        x for x in range(len(lines)) if (f"[ {section_name} ]" in lines[x].lower())
    ]
    idx_section_general = [x for x in range(len(lines)) if ("[ " in lines[x].lower())]
    start = idx_section[0]
    try:
        end = idx_section_general[idx_section_general.index(start) + 1]  # next '[' idx
        # data_target = lines[start:end]
    except IndexError:
        end = False
        # data_target = lines[start:]  # Not data[start:-1]
    return start, end, idx_section, idx_section_general


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
