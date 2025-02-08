from apps.shared.models.recipe import Recipe

recipe = Recipe(0)

def test_recipe_init() :
    r = Recipe(10)
    assert r.list_product == []
    assert r.id == 10

def test_add_product() :
    recipe.add_product("a", 10, 0.1)
    recipe.add_product("b", 100, 0.1)
    assert len(recipe.list_product) == 2
    assert recipe.list_product[0]["product"] == "a"
    assert recipe.list_product[0]["quantity_target"] == 10
    assert recipe.list_product[0]["quantity_min"] == 9
    assert recipe.list_product[0]["quantity_max"] == 11

def test_get_product() :
    products = recipe.get_products()
    assert len(products) == 2
    assert products[0]["product"] == "a"
    assert products[0]["quantity_target"] == 10
    assert products[0]["quantity_min"] == 9
    assert products[0]["quantity_max"] == 11

def test_get_recipe_by_product() : 
    product = recipe.get_product("b")
    assert product["product"] == "b"
    assert product["quantity_target"] == 100
    assert product["quantity_min"] == 90
    assert product["quantity_max"] == 110

def test_get_id() : 
    assert recipe.get_id() == 0

def test_print_recipe(capsys) :
    recipe.print_recipe()
    captured = capsys.readouterr()

    assert captured.out == "Recipe n° 0\nProduct : a, Quantity target : 10, Quantity min : 9.0, Quantity max : 11.0.\nProduct : b, Quantity target : 100, Quantity min : 90.0, Quantity max : 110.0.\n"