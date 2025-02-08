import math as m

class Recipe() :
    def __init__(self, id):
        self.list_product = []
        self.id = id

    def add_product(self, product, quantity, tolerance) :
        quantity_min = m.ceil(quantity * (1 - tolerance)*100)/100
        quantity_max = m.floor(quantity * (1 + tolerance)*100)/100
        quantity = round(quantity, 2)
        prod = {"product" : product, "quantity_target" : quantity, "quantity_min" : quantity_min, "quantity_max" : quantity_max}
        self.list_product.append(prod)
    
    def get_products(self) : 
        return self.list_product
    
    def get_product(self, product_name) : 
        for i in self.list_product :
            if i['product'] == product_name : 
                return i

    def get_id(self) : 
        return self.id

    def print_recipe(self) :
        print(f"Recipe n° {self.id}")
        for i in self.list_product :
            print(f"Product : {i['product']}, Quantity target : {i['quantity_target']}, Quantity min : {i['quantity_min']}, Quantity max : {i['quantity_max']}.")