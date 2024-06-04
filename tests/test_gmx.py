""" Test for moltopolparser.gmx module """

from typing import List

import pytest
from pydantic import ValidationError

from moltopolparser.gmx import (
    GroFileAtom,
    parse_gro_file,
    parse_top_file,
    MolTopAtom,
    MolTopDihedral,
)


def test_parse_gro_atom():
    """
    Test case for parsing a GRO file atom.
    """
    example_data = {
        "resid": 1,
        "resname": "H2O",
        "atom_name": "O",
        "index": 1,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "vx": 0.0,
        "vy": 0.0,
        "vz": 0.0
    }

    atom_instance = GroFileAtom(**example_data)
    assert atom_instance.resid == 1
    assert atom_instance.resname == "H2O"
    assert atom_instance.atom_name == "O"
    assert atom_instance.index == 1
    assert atom_instance.x == 0.0
    assert atom_instance.y == 0.0
    assert atom_instance.z == 0.0
    assert atom_instance.vx == 0.0
    assert atom_instance.vy == 0.0
    assert atom_instance.vz == 0.0


def test_parse_gro_atom_novelocity():
    """
    Test case for parsing a GRO file atom with no velocity given.
    """
    example_data = {
        "resid": 1,
        "resname": "H2O",
        "atom_name": "O",
        "index": 1,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
    }

    atom_instance = GroFileAtom(**example_data)
    assert atom_instance.resid == 1
    assert atom_instance.resname == "H2O"
    assert atom_instance.atom_name == "O"
    assert atom_instance.index == 1
    assert atom_instance.x == 0.0
    assert atom_instance.y == 0.0
    assert atom_instance.z == 0.0
    assert atom_instance.vx == 0.0
    assert atom_instance.vy == 0.0
    assert atom_instance.vz == 0.0


def test_parse_gro_atom_error():
    """
    Test case for parsing a GRO file atom with wrong resid type.
    """
    example_data_error = {
        "resid": "x",
        "resname": "H2O",
        "atom_name": "O",
        "index": 1,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "vx": 0.0,
        "vy": 0.0,
        "vz": 0.0
    }
    with pytest.raises(ValidationError):
        GroFileAtom(**example_data_error)


def test_parse_gro_file():
    """
    Test case for parsing a GRO file contains two water molecules.
    """
    file_names = ['two_water.gro',
                  'two_water_nobreakline.gro',
                  'two_water_extralines.gro']
    for file_name in file_names:
        input_file = f"./tests/data/gmx/{file_name}"
        gro_file = parse_gro_file(input_file)
        gro_atoms = gro_file.gro_atoms
        assert gro_file.sys_name == "MD of 2 waters, t= 0.0"
        assert gro_file.num_atoms == 6
        if isinstance(gro_atoms, List):
            assert gro_atoms[0].resid == 1
            assert gro_atoms[0].resname == "WATER"
            assert gro_atoms[0].atom_name == "OW1"
            assert gro_atoms[5].index == 6
            assert gro_atoms[5].resid == 2
            assert gro_atoms[5].resname == "WATER"
            assert gro_atoms[5].atom_name == "HW3"
            assert gro_atoms[5].vx == 1.9427
            assert gro_atoms[5].vy == -0.8216
            assert gro_atoms[5].vz == -0.0244
        else:
            raise TypeError("gro_atoms is not a list")


def test_parse_top_file():
    """
    Test case for parsing a GROMACS topology file.
    Currently only tested on Martini 2 topologies from the Charmmgui server.
    """
    input_file = './tests/data/gmx/membrane-martini-charmmgui/system.top'
    parse_top_file(input_file)


def test_MolTopAtom():
    """
    Test parse atom from data
    """
    atom_data = {
                "id": 10,
                "atom_type": "C",
                "resnr": 100,
                "residu": "UREA",
                "atom": "C1",
                "cgnr": 1,
                "charge": -0.683,
    }
    atom_instance = MolTopAtom(**atom_data)
    assert atom_instance.id == 10
    assert atom_instance.atom_type == "C"
    assert atom_instance.resnr == 100
    assert atom_instance.residu == "UREA"
    assert atom_instance.atom == "C1"
    assert atom_instance.cgnr == 1
    assert atom_instance.charge == -0.683


def test_MolTopAtom_error():
    """
    Test parse atom from data with pydantic validation error
    """
    atom_data_error = {
                "id": 'XX',
                "atom_type": "C",
                "resnr": 100,
                "residu": "UREA",
                "atom": "C1",
                "cgnr": 1,
                "charge": -0.683,
    }
    with pytest.raises(ValidationError):
        MolTopAtom(**atom_data_error)


def test_MolTopDihedral():
    """
    Test MolTopDihedral class
    """
    example_data_proper={
                "ai": 10,
                "aj": 21,
                "ak": 30,
                "al": 41,
                "func": 3,
                "c0": 11.0,
                "c1": 1.0,
                "c2": 2.0,
                "c3": 3.0,
                "c4": 4.0,
                "c5": 5.0,
    }
    dihedral = MolTopDihedral(**example_data_proper)
    assert dihedral.ai == 10
    assert dihedral.aj == 21
    assert dihedral.ak == 30
    assert dihedral.al == 41
    assert dihedral.func == 3
    assert dihedral.c0 == 11.0
    assert dihedral.c1 == 1.0
    assert dihedral.c2 == 2.0
    assert dihedral.c3 == 3.0
    assert dihedral.c4 == 4.0
    assert dihedral.c5 == 5.0
    
    example_data_proper_func4={
                "ai": 10,
                "aj": 21,
                "ak": 30,
                "al": 41,
                "func": 4,
                "c0": 11.0,
                "c1": 1.0,
    }
    dihedral = MolTopDihedral(**example_data_proper_func4)
    assert dihedral.ai == 10
    assert dihedral.aj == 21
    assert dihedral.ak == 30
    assert dihedral.al == 41
    assert dihedral.func == 4
    assert dihedral.c0 == 11.0
    assert dihedral.c1 == 1.0
    
    example_data_proper_func1={
                "ai": 10,
                "aj": 21,
                "ak": 30,
                "al": 41,
                "func": 1,
                "c0": 11.0,
                "c1": 1.0,
                "c2": 2.0,
    }
    dihedral = MolTopDihedral(**example_data_proper_func1)
    assert dihedral.ai == 10
    assert dihedral.aj == 21
    assert dihedral.ak == 30
    assert dihedral.al == 41
    assert dihedral.func == 1
    assert dihedral.c0 == 11.0
    assert dihedral.c1 == 1.0
    assert dihedral.c2 == 2.0


    example_data_improper={
                "ai": 10,
                "aj": 21,
                "ak": 30,
                "al": 41,
                "func": 1,
                "c0": 11.0,
                "c1": 1.0,
                "c2": 2.0,
                "c3": 3.0,
                "c4": 4.0,
                "c5": 5.0,
    }
    with pytest.raises(ValidationError):
        dihedral = MolTopDihedral(**example_data_improper)