## pip install -i https://test.pypi.org/simple/ moltopolparser
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
        "vz": 0.0,
    }

atom_data = {
        "id": 10,
        "atom_type": "C",
        "resnr": 100,
        "residu": "UREA",
        "atom": "C1",
        "cgnr": 1,
        "charge": -0.683,
}
### 
from moltopolparser.gmx import GroAtom
from moltopolparser.gmx import MolTopAtom
atom_instance =  GroAtom(**example_data)
print(atom_instance)
atom_instance2 = MolTopAtom(**atom_data)
print(atom_instance2)
### 
import moltopolparser as mtp
atom_instance = mtp.gmx.GroAtom(**example_data)
atom_instance2 = mtp.gmx.MolTopAtom(**atom_data)
print(atom_instance)
print(atom_instance2)

