import numpy as np
import pytest
from apps.shared.models import batch, storage

# Importer les fonctions à tester depuis votre module.
# Adaptez le chemin d'import à votre projet.
from apps.shared.models.solver import (
    split_array,
    solve,
    update_matrix_decision,
    create_block_diagonal,
    find_vials_matrix_test,
    clean_matrix,
    verifying_number_of_vial_by_recipe,
    fusion_array,
    creation_list_id,
    fusion_dictionary_by_product,
    creation_list_missing_elements,
    calcul_quantities,
)

class DummyVial:
    def __init__(self, id, quantity, product):
        self._id = id
        self._quantity = quantity
        self._product = product

    def get_quantity(self):
        return self._quantity

    def get_id(self):
        return self._id

    def get_product(self):
        return self._product

class DummyStorage:
    def __init__(self, vials):
        self.vials = vials

    def get_vials(self):
        return self.vials

    def get_vials_by_product(self, product):
        return [v for v in self.vials if v.get_product() == product]

    def get_vials_by_id(self, id):
        for vial in self.vials:
            if vial.get_id() == id:
                return vial
        return None

class DummyRecipe:
    def __init__(self, id, product_info):
        self._id = id
        self._product_info = product_info

    def get_id(self):
        return self._id

    def get_products(self):
        return self._product_info

class DummyBatch:
    def __init__(self, products, recipes):
        """
        products : liste de noms de produits, ex: ['A']
        recipes : liste de tuples (id, product_info)
        """
        self.products = products
        self.recipes = recipes

    def get_list_products(self):
        return self.products

    def get_recipes(self):
        return [DummyRecipe(r[0], r[1]) for r in self.recipes]

    def get_recipes_by_product(self, product):
        return [r for r in self.recipes if r[1].get('product') == product]
def test_split_array_with_list():
    arr = [1, 2, 3, 4, 5, 6]
    result = split_array(arr, 3)
    assert result == [[1, 2, 3], [4, 5, 6]]

def test_split_array_with_numpy_array():
    arr = np.array([1, 2, 3, 4, 5, 6])
    result = split_array(arr, 2)
    result_as_list = [chunk.tolist() for chunk in result]
    assert result_as_list == [[1, 2], [3, 4], [5, 6]]

def test_update_matrix_decision():
    A = np.zeros((2, 5))
    list_ids = [[2, 3], [5]]
    list_recipes = [(0, {}), (1, {})]
    updated_A = update_matrix_decision(A.copy(), list_ids, list_recipes)
    expected = np.zeros((2, 5))
    expected[0, 1] = 1
    expected[0, 2] = 1
    expected[1, 4] = 1
    np.testing.assert_array_equal(updated_A, expected)

def test_create_block_diagonal():
    pattern = np.array([[1, 2], [3, 4]])
    nbreRecipes = 3
    sizeStorage = 4
    result = create_block_diagonal(pattern, nbreRecipes, sizeStorage)
    assert result.shape == (6, 12)
    for i in range(nbreRecipes):
        start_row = i * pattern.shape[0]
        start_col = i * sizeStorage
        block = result[start_row:start_row+pattern.shape[0], start_col:start_col+pattern.shape[1]]
        np.testing.assert_array_equal(block, pattern)

def test_clean_matrix():
    matrix = [
        [1, -1, 2],
        [-1, -1, 3],
        [4, 5, -1]
    ]
    cleaned = clean_matrix(matrix)
    expected = [
        [1, 2],
        [3],
        [4, 5]
    ]
    assert cleaned == expected

def test_verifying_number_of_vial_by_recipe():
    decision_matrix = np.array([
        [1, 1, 1, 0],
        [0, 1, 0, 0]
    ])
    reactor_capacity = 2
    unfeasible, updated_matrix = verifying_number_of_vial_by_recipe(decision_matrix.copy(), reactor_capacity)
    np.testing.assert_array_equal(updated_matrix[0], np.zeros(4))
    np.testing.assert_array_equal(updated_matrix[1], decision_matrix[1])
    assert unfeasible == [0]

def test_fusion_array():
    array_1 = [(1, {'product': 'A'}), (2, {'product': 'B'})]
    array_2 = [(2, {'product': 'B'}), (3, {'product': 'C'})]
    result = fusion_array(array_1.copy(), array_2)
    ids = {entry[0] for entry in result}
    assert ids == {1, 2, 3}

def test_creation_list_id():
    decision_matrix = np.array([
        [1, 0, 1, 0],
        [0, 1, 0, 0]
    ])
    result = creation_list_id(decision_matrix)
    expected = [([0, 2], 0), ([1], 1)]
    assert result == expected

def test_fusion_dictionary_by_product():
    input_list = [
        {'product': 'A', 'quantity': 10},
        {'product': 'B', 'quantity': 5},
        {'product': 'A', 'quantity': 7},
    ]
    result = fusion_dictionary_by_product(input_list)
    result_dict = {entry['product']: entry['quantities'] for entry in result}
    assert 'A' in result_dict and 'B' in result_dict
    assert sorted(result_dict['A']) == [7, 10]
    assert result_dict['B'] == [5]

def test_creation_list_missing_elements():
    unfeasible_recipes = [
        (0, {'product': 'A', 'quantity_target': 10}),
        (1, {'product': 'B', 'quantity_target': 5}),
    ]
    ids, missing = creation_list_missing_elements(unfeasible_recipes)
    assert ids == [0, 1]
    missing_products = {elem['product'] for elem in missing}
    assert missing_products == {'A', 'B'}

def test_calcul_quantities():
    list_id = [
        ([1, 2], 0),
        ([3], 1)
    ]
    vial1 = DummyVial(1, 10, 'A')
    vial2 = DummyVial(2, 15, 'A')
    vial3 = DummyVial(3, 20, 'B')
    storage = DummyStorage([vial1, vial2, vial3])
    list_unfeasible_recipe = [
        (1, {'product': 'B', 'quantity_target': 5})
    ]
    quantities = calcul_quantities(storage, list_id, list_unfeasible_recipe)

    expected = [
        ({'A': 25}, 0),
        ({'B': 0}, 1)
    ]
    assert quantities == expected

def test_split_array_empty():
    arr = []
    result = split_array(arr, 3)
    assert result == []

def test_create_block_diagonal_with_zero_recipes():
    pattern = np.array([[1, 2], [3, 4]])
    result = create_block_diagonal(pattern, 0, 5)
    assert result.size == 0

def test_update_matrix_decision_empty_ids():
    A = np.zeros((1, 3))
    list_ids = [[]]
    list_recipes = [(0, {})]
    updated_A = update_matrix_decision(A.copy(), list_ids, list_recipes)
    np.testing.assert_array_equal(updated_A, A)

def test_find_vials() : 
    recipes = [{"chemical element":"Farine", "quantity":10, "tolerance":0.1}]
    b = batch.Batch()
    b.add_recipe(recipes)

    s = storage.Storage()
    s.generate_vials("Farine", 10, 0)
    decision_matrix, slack_variable, status = find_vials_matrix_test(b.get_recipes_by_product("Farine"), s.get_vials(), 2)

    assert status == 0
    assert slack_variable == [0]
    assert decision_matrix == [[0]]

def test_solve() : 
    recipes = [{"chemical element":"Farine", "quantity":10, "tolerance":0.1}]
    b = batch.Batch()
    b.add_recipe(recipes)

    s = storage.Storage()
    s.generate_vials("Farine", 10, 0)
    list_id, quantities, id_undeasible_recipe, missing_elements = solve(b, s, 2)
    print(quantities)
    print(id_undeasible_recipe)
    print(missing_elements)
    assert list_id == [([0], 0)]
    assert quantities ==  [({'Farine' : 10}, 0)]
    assert id_undeasible_recipe == []
    assert missing_elements == []
