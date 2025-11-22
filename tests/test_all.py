from padelpy2 import Calculator, descriptors, descriptors_2d, descriptors_3d, \
    fingerprints


def test_2d_descriptor_generation(test_molecules):

    calc = Calculator(descriptors_2d)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 1444


def test_3d_descriptor_generation(test_molecules):

    calc = Calculator(descriptors_3d)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 431


def test_all_descriptor_generation(test_molecules):

    calc = Calculator(descriptors)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 1875


def test_fingerprints(test_molecules):

    for fp in fingerprints:
        calc = Calculator([fp])
        results = calc(test_molecules)
        assert results.shape[0] == len(test_molecules)
        assert results.shape[1] == fp.n_bits
