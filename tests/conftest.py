from typing import List

import pytest
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem import rdDistGeom


@pytest.fixture(scope="session")
def test_molecules() -> List[str]:

    smiles = [
        "CN=C=O",
        "CC(=O)NCCC1=CNc2c1cc(OC)cc2",
        "OCCc1c(C)[n+](cs1)Cc2cnc(C)nc2N",
    ]
    mols = [Chem.AddHs(Chem.MolFromSmiles(smi)) for smi in smiles]
    for mol in mols:
        rdDepictor.Compute2DCoords(mol)
        rdDistGeom.EmbedMolecule(mol)
    return mols
