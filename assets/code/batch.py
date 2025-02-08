from . import recipe as r, read_write_data as rw
import numpy as np
import pandas as pd

class Batch() : 
    """
    Represents a collection of recipes, enabling recipe generation, management, and querying.

    Attributes:
        recipes (list): A list that stores all recipes created in the batch.
    """
    def __init__(self):
        """
        Initializes the Batch object with an empty list of recipes.
        """
        self.recipes = []
        self.list_product = []

    def get_recipes(self) :
        """
        Retrieves the list of all recipes in the batch.

        Returns:
            list: A list of Recipe objects.
        """
        return self.recipes
    
    def get_recipes_by_product(self, product) :
        """
        Retrieves recipes containing a specific product.

        Args:
            product: The product to search for in the recipes.

        Returns:
            None
        """ 
        selected_recipes = [(recipe.get_id(), recipe.get_product(product)) for _, recipe in enumerate(self.recipes) if recipe.get_product(product) != None]
        return selected_recipes

    def get_list_products(self) :
        return self.list_product

    def print(self) :
        for i in self.recipes :
            i.print_recipe()


    def add_recipe(self, list_product) :
        """
        Adds a new recipe to the batch based on a list of products.

        Args:
            list_product (list): A list of dictionaries, each containing:
                - 'product': The name or identifier of the product.
                - 'qty': The quantity of the product.
                - 'tolerance': The tolerance allowed for the quantity.

        Returns:
            None
        """ 
        recipe = r.Recipe(len(self.recipes))
        for i in list_product :
            product = i["chemical element"]
            quantity = i ["quantity"]
            tolerance = i ["tolerance"]
            recipe.add_product(product, quantity, tolerance)
            if product not in self.list_product :
                self.list_product.append(product)

        self.recipes.append(recipe)
    
    def generate_batch_from_dataframe(self, df) :
        self.list_product = df['chemical element'].drop_duplicates().tolist()
        nbre_recipes = df['n° recipe'].max()
        
        for i in range(1, nbre_recipes+1) :
            filtered_data = df[df['n° recipe'] == i]
            result = tuple({col : row[col] for col in df.columns} for _, row in filtered_data .iterrows())
            self.add_recipe(result)

    def generate_batch_from_excel(self, path, filename) :
        df = pd.read_excel(path + filename, index_col=None)
        self.generate_batch_from_dataframe(df)