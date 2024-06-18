import moltopolparser as mtp

# ----------------------------- Base data direct validation
atom_data = {
        "id": 10,
        "atom_type": "C",
        "resnr": 100,
        "residu": "UREA",
        "atom": "C1",
        "cgnr": 1,
        "charge": -0.683,
    }
atom = mtp.gmx.MolTopAtom(**atom_data)
# print(atom.charge) # -> -0.683


# -------------------------  Access via parsing a single file
gro_file = '../tests/data/gmx/two_water.gro'
gro = mtp.gmx.GroFile.parser(gro_file)
# print(gro.box_size) # -> [1.8206, 1.8206, 1.8206]

# ----------------------- Access via parsing top files, see example file below
top_file = '../tests/data/gmx/membrane-martini-charmmgui/system.top'
sys_top = mtp.gmx.Topology.parser(top_file)
# print(sys_top.system) # -> Martini system

sys_top.pull_forcefield()
print(sys_top.forcefield.atomtypes[0]) 
# -> name='P5' at_num=None mass=72.0 charge=0.0 ptype='A' sigma=0.0 epsilon=0.0

sys_top.pull_molecule_topologies()
print(sys_top.molecule_topologies[0])
# header=MolTopHeader(name='W', nrexcl=1) atoms=[MolTopAtom(id=1, atom_type='P4', resnr=1, residu='W', atom='W', cgnr=1, charge=0.0)]
# bonds=None pairs=None angles=None dihedrals=None