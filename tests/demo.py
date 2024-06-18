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
print(atom.charge)

# -------------------------  Access via parsing a single file
gro_file = './tests/data/gmx/two_water.gro'
gro = mtp.gmx.GroFile.parse(gro_file)
print(gro.box_size)


# ----------------------- Access via parsing top files, see example file below
top_file = './tests/data/gmx/membrane-martini-charmmgui/system.top'
sys_top = mtp.gmx.Topology.parser(top_file)
print(sys_top.system)

sys_top.pull_forcefield()
print(sys_top.forcefield.atomtypes)

sys_top.pull_molecule_topologies()
print(sys_top.molecule_topologies)


