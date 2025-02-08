
import pandas as pd
from apps.shared.models.storage import Storage

storage = Storage()

def test_storage_init() :
    assert storage.vials == []

def test_generate_vials() :
    storage.generate_vials("a", 1, 0)

    assert len(storage.vials) == 1

def test_get_vials(capsys) :
    assert len(storage.get_vials()) == 1

    storage.generate_vials("b", 1, 2)
    assert len(storage.get_vials()) == 2

    (storage.get_vials()[0]).print_caracteristique()
    captured = capsys.readouterr()
    assert captured.out == "product : a qty : 1 id : 0\n"
    (storage.get_vials()[1]).print_caracteristique()
    captured = capsys.readouterr()
    assert captured.out == "product : b qty : 1 id : 2\n"

def test_get_vials_by_product() :
    vials_a = storage.get_vials_by_product("a")
    vials_b = storage.get_vials_by_product("b")
    vials_c = storage.get_vials_by_product("c")

    for vial in vials_a :
        assert vial.get_product() == "a"
    
    for vial in vials_b :
        assert vial.get_product() == "b"

    assert vials_c == []

def test_get_vial_by_id() : 
    vial0 = storage.get_vials_by_id(0)
    vial1 = storage.get_vials_by_id(1)
    vial2 = storage.get_vials_by_id(2)

    assert vial0.get_id() == 0
    assert vial1 == None
    assert vial2.get_id() == 2

def test_print_storage(capsys) :
    storage.print_storage()

    captured = capsys.readouterr()
    assert captured.out == "product : a qty : 1 id : 0\nproduct : b qty : 1 id : 2\n"

def test_generation_with_dataframe() : 
    new_storage = Storage()
    parameters = [0, 7, "drawer", "Standardization", "caps", "sodium fluoride", "7681-49-4", 
                  "SwissCAT-649433", "[F-].[Na+]", "1S/FH.Na/h1H;/q;+1/p-1", "NaF", 41.99, 
                  2.56, 3.327]
     
    df = pd.DataFrame(columns=["vialID", "vialGloveBoxLocationID", "vialGloveBoxLocationName", "gloveBox", 
                               "vialType", "Chemical name", "CAS Number", "SwissCATNumber", "Smiles", "Inchi", 
                               "Molecular formula", "Molecular mass [g/mol]", "Density [mg/L]", "Quantity [mg]"])
    df.loc[0] = parameters

    new_storage.generate_storage_from_df(df)
    assert len(new_storage.get_vials()) == 1
    vial = new_storage.get_vials()[0]
    assert vial.get_id() == parameters[0]
    assert vial.get_product() == parameters[5]
    assert vial.get_quantity() == parameters[-1]

def test_generation_with_excel() : 
    parameters = [7014, 7, "drawer", "Standardization", "caps", "sodium fluoride", "7681-49-4", 
                  "SwissCAT-649433", "[F-].[Na+]", "1S/FH.Na/h1H;/q;+1/p-1", "NaF", 41.99, 
                  2.56, 3.327]
    new_storage = Storage()
    path = "tests/input/data_base/"
    new_storage.generate_storage_from_excel(path, 'vial', {'vialType':'caps'})

    assert len(new_storage.get_vials()) == 1
    vial = new_storage.get_vials()[0]
    assert vial.get_id() == parameters[0]
    assert vial.get_product() == parameters[5]
    assert vial.get_quantity() == parameters[-1]
    
    parameters = [7014, 7, "drawer", "Standardization", "caps", "sodium fluoride", "7681-49-4", 
                  "SwissCAT-649433", "[F-].[Na+]", "1S/FH.Na/h1H;/q;+1/p-1", "NaF", 41.99, 
                  2.56, 3.327]
    new_storage2 = Storage()
    path = "tests/input/data_base/"
    new_storage2.generate_storage_from_excel(path, 'vial')

    assert len(new_storage2.get_vials()) == 1
    vial2 = new_storage2.get_vials()[0]
    assert vial2.get_id() == parameters[0]
    assert vial2.get_product() == parameters[5]
    assert vial2.get_quantity() == parameters[-1]
