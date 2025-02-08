class Vials() :
    """
    Represents a vial containing a specific product with a defined quantity and unique identifier.

    Attributes:
        product: The name or identifier of the product contained in the vial.
        quantity (float): The quantity of the product in the vial.
        id (int): A unique identifier for the vial.
    """
    def __init__(self, product, quantity, id) :
        """
        Initializes a Vials object with the specified product, quantity, and id.
        
        Args:
            product: The name or identifier of the product contained in the vial.
            quantity (float): The quantity of the product in the vial. Must be greater than 0.
            id (int): The unique identifier for the vial. Must be 0 or greater.

        Raises:
            ValueError: If the quantity is less than or equal to 0.
            ValueError: If the id is less than 0.
        """
        if (quantity <= 0) :
            raise ValueError("The quantity in vial can't be negative or egals to 0.")
        if (id < 0) :
            raise ValueError("The id of vial must be superior to 0.")
        self.product = product
        self.quantity = quantity
        self.id = id

    def get_quantity(self) :
        """
        Retrieves the quantity of the product in the vial.

        Returns:
            float: The quantity of the product.
        """ 
        return self.quantity
    
    def get_id(self) :
        """
        Retrieves the unique identifier of the vial.

        Returns:
            int: The unique identifier of the vial.
        """
        return self.id

    def get_product(self) :

        return self.product
    def print_caracteristique(self) :
        """
        Prints the characteristics of the vial, including the product name, quantity, and id.

        Returns:
            None
        """
        print(f"product : {self.product} qty : {self.quantity} id : {self.id}")
