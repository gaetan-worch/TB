import random
import pandas as pd

from . import vials, read_write_data as rwd

class Storage() :
    """
    Represents a storage system for vials, allowing the generation, management, 
    and querying of vials with specific properties.

    Attributes:
        vials (list): A list that stores all vials in the storage.
    """
    def __init__(self):
        """
        Initializes the Storage object with an empty list of vials.
        """
        self.vials = []

    def generate_vials(self, product, qty, numero) :
        """
        Creates a single vial and adds it to the storage.

        Args:
            product: The name or identifier of the product contained in the vial.
            qty (float): The quantity of the product in the vial.
            numero (int): The unique identifier for the vial.

        Returns:
            None
        """
        self.vials.append(vials.Vials(product, qty, numero))

    def get_vials(self) :
        """
        Retrieves the list of all vials in the storage.

        Returns:
            list: A list of Vials objects.
        """ 
        return self.vials
    
    def get_vials_by_product(self, product) :
        """
        Return the list of vials 

        Args :
            product : the product a selected
        """
        vial_returned = [self.vials[i] for i in range(len(self.vials)) if self.vials[i].get_product() == product]
        return vial_returned
    
    def get_vials_by_id(self, id) : 
        for i in self.vials :
            if i.get_id() == id :
                return i

        return None

    def print_storage(self) :
        """
        Prints the characteristics of all vials in the storage.

        Returns:
            None
        """
        for i in range(len(self.vials)) :
            self.vials[i].print_caracteristique()   

    def generate_storage_from_df(self, df) :
        """
        Generate the storage from a data_frame

        Parameters :
            df (data_frame) : A data_frame with the storage

        Return:
            None
        """
        for _, row in df.iterrows() :
            self.generate_vials(row["Chemical name"], row["Quantity [mg]"], row["vialID"])

    def generate_storage_from_excel(self, path, data_type, filters=None) :
        """
        Generate storage from excel file

        Parameters : 
            path (string) : The path where search storage file
            data_type (string) : The data selection sheet
            filters (dictionnary) : The various filters to select data ({'column name':'valeur'})
        """
        data = rwd.Data(path)
        if not filters == None :
            data = data.get_filtered_data(data_type, filters)
        else :
            data = data.get_df(data_type)
        self.generate_storage_from_df(data)