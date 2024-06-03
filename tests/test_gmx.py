""" Test for moltopolparser.gmx module """

from typing import List

import pytest
from pydantic import ValidationError

from moltopolparser.gmx import GroFileAtom, parse_gro_file, parse_top_file_shallow


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


def test_parse_top_file_shallow():
    """
    Test case for parsing a GROMACS topology file.
    Currently only tested on Martini 2 topologies from the Charmmgui server.
    """
    input_file = './tests/data/gmx/membrane-martini-charmmgui/system.top'
    parse_top_file_shallow(input_file)
