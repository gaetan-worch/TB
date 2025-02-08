from ortools.linear_solver import pywraplp
import numpy as np
from ..models import batch as b, storage as s    

def split_array(arr, chunk_size) :
    """
    Splits a list `arr` into smaller sublists (chunks) of a specified size (`chunk_size`).
    
    Parameters:
        arr (list): List of elements to be split.
        chunk_size (int): The size of each chunk (sublist).
    
    Returns:
        list: A list of sublists, each containing at most `chunk_size` elements from the original list.
    """
    return [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]

def solve(batch, storage, reactor_capacity) :
    """
    Solves the optimization problem related to vial assignment, using a decision matrix 
    and considering constraints on product quantities.
    
    Parameters:
        batch (object): An object representing a batch with products and recipes.
        storage (object): An object representing the storage containing vials.
    
    Returns:
        tuple: A tuple containing:
            - list_id (list): A list of the decision matrix.
            - quantities (list): A list of quantities calculated based on the decision matrix.
            - id_unfeasible_recipe (list): The IDs of recipes that could not be completed.
            - missing_elements (list): A list of missing products/quantities for unfeasible recipes.
    """
    list_id = []
    list_product = batch.get_list_products()
    list_recipes_no_solution = []
    all_recipes = batch.get_recipes()
    decision_matrix = np.zeros([len(all_recipes), len(storage.get_vials())])
    nbre_product = len(list_product)
    for i in range(nbre_product) : 
        product = list_product[i]
        recipes = batch.get_recipes_by_product(product)
        while(True) :
            recipes = [recipe for recipe in recipes if recipe not in list_recipes_no_solution]
            decision_matrix_solver, slack_variable, status = find_vials_matrix_test(recipes, storage.get_vials_by_product(product), nbre_vial_maxium_per_reactor=reactor_capacity)
            if sum(slack_variable) == 0 :
                break
            index_max = np.argmax(slack_variable)
            list_recipes_no_solution.append(recipes[index_max])
        cleaned_matrix = clean_matrix(decision_matrix_solver)
        list_id.append(cleaned_matrix)
        
        decision_matrix = update_matrix_decision(decision_matrix, cleaned_matrix, recipes)
    recipe_with_too_much_vials, decision_matrix = verifying_number_of_vial_by_recipe(decision_matrix, reactor_capacity)
    list_recipe_too_much_microcaps = [(all_recipes[i].get_id(), all_recipes[i].get_products()) for i in range(len(all_recipes)) if all_recipes[i].get_id() in recipe_with_too_much_vials]
    
    list_unfeasible_recipes = fusion_array(list_recipe_too_much_microcaps, list_recipes_no_solution)
    id_unfeasible_recipe, missing_elements = creation_list_missing_elements(list_unfeasible_recipes)
    list_id = creation_list_id(decision_matrix)
    quantities = calcul_quantities(storage, list_id, list_unfeasible_recipes)
    return list_id, quantities, id_unfeasible_recipe, missing_elements

def update_matrix_decision(A, list_ids, list_recipes) :
    """
    Updates a decision matrix `A` based on selected IDs from `list_ids` and corresponding recipes in `list_recipes`.
    
    Parameters:
        A (ndarray): The decision matrix to be updated.
        list_ids (list): A list of selected IDs.
        list_recipes (list): A list of recipes.
    
    Returns:
        ndarray: The updated decision matrix `A`.
    """
    
    for index, recipe in enumerate(list_recipes):
        num_recipe = recipe[0]
        for i in list_ids[index] :
            A[num_recipe, i-1] = 1

    return A

def create_block_diagonal(pattern, nbreRecipes, sizeStorage):
    """
    Creates a block diagonal matrix based on a given pattern, repeating it for a specified number of recipes and storage size.
    
    Parameters:
        pattern (ndarray): A 2D array representing the pattern to be repeated.
        nbreRecipes (int): The number of recipes (how many times the pattern should be repeated).
        sizeStorage (int): The size of the storage.
    
    Returns:
        ndarray: A 2D matrix where the given pattern is repeated diagonally.
    """
    block_rows, block_cols = pattern.shape

    rows = nbreRecipes * block_rows
    cols = nbreRecipes * sizeStorage

    result = np.zeros((rows, cols))

    for i in range(nbreRecipes):
        start_row = i * block_rows
        start_col = i * sizeStorage
        result[start_row:start_row + block_rows, start_col:start_col + block_cols] = pattern

    return result

def find_vials_matrix_test(recipes, stock, nbre_vial_maxium_per_reactor):
    """
    Solves an optimization problem using the Google OR-Tools solver to assign vials to recipes while considering the constraints.
    
    Parameters:
        recipes (list): A list of recipes with product quantities.
        stock (list): The list of available vials in storage.
        nbre_vial_maxium_per_reactor (int): The maximum number of vials allowed per reactor.
    
    Returns:
        tuple: A tuple containing:
            - split_soluce_ids (list): Solution IDs for the vials assigned to the recipes.
            - z_sum (list): A list of slack variables (unused quantities).
            - status (int): The status of the solver (optimal, infeasible, etc.).
    """
    nbre_recipes = len(recipes)
    size_storage = len(stock)
    m1 = np.zeros([2, size_storage])
    for index, vial in enumerate(stock) :
        m1[0, index] = vial.get_quantity()
        m1[1, index] = -vial.get_quantity()
    
    I = np.identity(size_storage)
    nbre_rep_I_block = nbre_recipes
    I_block = np.tile(I, (1, nbre_rep_I_block))
    qty_bounds = np.zeros([0, 0])
    for index, recipe in enumerate(recipes) :
        product = recipe[1]
        y = np.array([[product['quantity_max'], -product['quantity_min']]])
        qty_bounds = np.append(qty_bounds, y)
    A = np.block([[m1 if i == j else np.zeros_like(m1) for i in range(nbre_recipes)] for j in range(nbre_recipes)])
    
    b = np.ones([1, nbre_recipes + size_storage])
    b[:, 0:nbre_recipes] = nbre_vial_maxium_per_reactor

    B = np.zeros([nbre_recipes, nbre_recipes*size_storage])

    for i in range(nbre_recipes) : 
        B[i, i*size_storage:i*size_storage+size_storage] = 1

    B = np.append(B, I_block, axis = 0)

    pattern = np.array([[1 for _ in range(size_storage)], [-1 for _ in range(size_storage)]])
    C = create_block_diagonal(pattern, nbre_recipes, size_storage)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    x = [solver.IntVar(0, 1, f"x{i}") for i in range(nbre_recipes*size_storage)]
    y = [solver.NumVar(-solver.infinity(), solver.infinity(), f"y{i}") for i in range(nbre_recipes*size_storage)]
    for i in range(len(qty_bounds)) :
        solver.Add(solver.Sum(A[i, j] * x[j] + C[i, j] * y[j] for j in range(len(x))) <= qty_bounds[i])
    for i in range(B.shape[0]) :
        solver.Add(solver.Sum(B[i, j] * x[j] for j in range(len(x))) <= b[0][i])
    
    z = [solver.NumVar(0, solver.infinity(), f"z{i}") for i in range(len(y))]
    for i in range(len(y)):
        solver.Add(z[i] >= y[i])
        solver.Add(z[i] >= -y[i])
    solver.SetTimeLimit(3600000)
    solver.Minimize(solver.Sum(x) + 100*solver.Sum(z))
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        soluce_ids = [int(x[i].solution_value() * stock[i%len(stock)].get_id()) if x[i].solution_value() == 1 else -1 for i in range(len(x))]
        split_soluce_ids = split_array(soluce_ids, size_storage)
        z_value = [z[i].solution_value() for i in range(len(z))]
        split_slack_variable = split_array(z_value, size_storage)
        z_sum = [sum(split_slack_variable[i]) for i in range(len(split_slack_variable))] 
        return split_soluce_ids, z_sum, status
    elif status == pywraplp.Solver.INFEASIBLE:
        print("Problème infaisable : aucune solution ne respecte toutes les contraintes.")
    elif status == pywraplp.Solver.UNBOUNDED:
        print("Le problème est non borné.")
    elif status == pywraplp.Solver.ABNORMAL:
        print("Arrêt anormal du solveur.")
    elif status == pywraplp.Solver.NOT_SOLVED:
        print("Le problème n'a pas encore été résolu.")
    else:
        print("Statut inconnu.")
    return []

def clean_matrix(matrix) : 
    """
    Cleans the decision matrix by removing `-1` values (representing unassigned vials).
    
    Parameters:
        matrix (list): The decision matrix to be cleaned.
    
    Returns:
        list: A cleaned decision matrix without `-1` values.
    """
    filtred_matrix = []
    for i in range(len(matrix)) :
        filetered_line = []
        line = matrix[i]
        for j in range(len(line)) :
            if line[j] != -1 :
                filetered_line.append(line[j])
        
        filtred_matrix.append(filetered_line)
    return filtred_matrix

def verifying_number_of_vial_by_recipe(decision_matrix, nbre_vial_maximum_per_reactor) : 
    """
    Verifies that the number of vials per recipe does not exceed the specified limit.
    
    Parameters:
        decision_matrix (numpy array): The decision matrix indicating vial assignments to recipes.
        nbre_vial_maximum_per_reactor (int): The maximum allowed number of vials per reactor.
    
    Returns:
        tuple: A tuple containing:
            - unfeasible_recipe (list): A list of recipes that exceeded the vial limit.
            - decision_matrix (list): The updated decision matrix.
    """
    unfeasible_recipe = []
    for i in range(decision_matrix.shape[0]) :
        if np.sum(decision_matrix[i]) > nbre_vial_maximum_per_reactor :
            decision_matrix[i] = 0
            unfeasible_recipe.append(i)

    return unfeasible_recipe, decision_matrix

def fusion_array(array_1, array_2) :
    """
    Merges two arrays, ensuring no duplicate entries based on the first element (ID).
    
    Parameters:
        array_1 (list): The first array.
        array_2 (list): The second array.
    
    Returns:
        list: A merged array without duplicate entries.
    """
    index_array = {entry[0] for entry in array_1}

    for entry in array_2 :
        if entry[0] not in index_array : 
            array_1.append(entry)

    return array_1

def creation_list_id(decision_matrix) : 
    """
    Creates a list of IDs from the decision matrix, mapping recipes to their corresponding vials.
    
    Parameters:
        decision_matrix (list): The decision matrix indicating vial assignments to recipes.
    
    Returns:
        list: A list of tuples, where each tuple contains a list of vial IDs assigned to a recipe and the recipe's index.
    """
    array_id = []
    for i in range(decision_matrix.shape[0]) : 
        array_id_by_recipes = []
        for j in range(decision_matrix.shape[1]) : 
            if decision_matrix[i][j] == 1 :
                array_id_by_recipes.append(j)

        array_id.append((array_id_by_recipes, i))
    return array_id

def fusion_dictionary_by_product(dict) :
    """
    Merges a dictionary of products and quantities into a new structure, grouping quantities by product.
    
    Parameters:
        dict (list): A list of dictionaries containing products and their quantities.
    
    Returns:
        list: A list of dictionaries, each containing a product and its corresponding list of quantities.
    """
    all_products = {}
    for element in dict :
        product = element['product']
        quantity = element['quantity']
        if product not in all_products :
            all_products[product] = []
        all_products[product].append(quantity)
    fusionned_dictionnary = [{'product': product, 'quantities': quantities} for product, quantities in all_products.items()]
    return fusionned_dictionnary

def creation_list_missing_elements(list_unfeasible_recipes) : 
    """
    Creates a list of missing elements (products and quantities) for unfeasible recipes.
    
    Parameters:
        list_unfeasible_recipes (list): A list of unfeasible recipes.
    
    Returns:
        tuple: A tuple containing:
            - index_unfeasible_recipe (list): A list of unfeasible recipe IDs.
            - missing_element (list): A list of missing product quantities for each unfeasible recipe.
    """
    index_unfeasible_recipe = []
    missing_element = []
    for _, recipe in enumerate(list_unfeasible_recipes) : 
        index = recipe[0]
        products = [recipe[1]] if isinstance(recipe[1], dict) else recipe[1]
        index_unfeasible_recipe.append(index)
        for i in range(len(products)) :
            missing_element.append({'product':products[i]['product'], 'quantity':products[i]['quantity_target']})

    return index_unfeasible_recipe, missing_element

def calcul_quantities(storage, list_id, list_unfeasible_recipe) :
    """
    Calculates the quantities of products that are required based on the storage and recipe data.
    
    Parameters:
        storage (object): The storage object containing vial data.
        list_id (list): A list of IDs representing the decision matrix.
        list_unfeasible_recipe (list): A list of unfeasible recipes.
    
    Returns:
        list: A list of calculated quantities for the unfeasible recipes.
    """
    quantities = []
    for i in list_id :
        ids = i[0]
        num_recip = i[1]
        products = {}
        for id in ids :
            microcapsule = storage.get_vials_by_id(id)
            product = microcapsule.get_product()
            quantity = microcapsule.get_quantity()
            if product not in products :
                products[product] = 0
            products[product] += quantity
        quantities.append((products, num_recip))

    for unfeasible in list_unfeasible_recipe :
        num__unfeasible_recipe = unfeasible[0]
        products = [unfeasible[1]] if isinstance(unfeasible[1], dict) else unfeasible[1]
        for i, (product, idx) in enumerate(quantities) :
            if idx == num__unfeasible_recipe :
                for i in range(len(products)) :
                    product[products[i]['product']] = 0
    return quantities