from apps.shared.models.batch import Batch

batch = Batch()

def test_batch_init() :
    b = Batch()

    assert b.recipes == []
    assert b.list_product == []

def test_generate_batch() :
    path = "tests/input/recipe/"
    filename = "chemical_recipes_test.xlsx"
    batch.generate_batch_from_excel(path, filename)

    assert len(batch.recipes) == 1
    product = batch.recipes[0].get_products()[0]
    assert product["product"] == "Farine"
    assert product["quantity_target"] == 51236
    assert product["quantity_min"] == 46112.4
    assert product["quantity_max"] == 56359.6

def test_get_recipes() :
    products = batch.get_recipes()
    product = products[0].get_products()
    assert len(products) == 1
    assert product[0]["product"] == "Farine"
    assert product[0]["quantity_target"] == 51236
    assert product[0]["quantity_min"] == 46112.4
    assert product[0]["quantity_max"] == 56359.6

def test_get_recipes_by_product() :
    products_farine = batch.get_recipes_by_product("Farine")
    products_surce = batch.get_recipes_by_product("Sucre")

    assert len(products_farine) == 1
    assert len(products_surce) == 0 

def test_get_list_product() : 
    products = batch.get_list_products()

    assert products == ["Farine"]

def test_print(capsys) : 
    batch.print()
    captured = capsys.readouterr()

    assert captured.out == "Recipe n° 0\nProduct : Farine, Quantity target : 51236, Quantity min : 46112.4, Quantity max : 56359.6.\n"
