import pandas as pd
import os
import time

FIRST_SHEET_NAME = "Plates"
SECOND_SHEET_NAME = "Vials_Caps"
NAMEFILE = "_Output"

class Data :
    """
    This class provide functionality to manage and manipulate Excel data related to plate and vials/caps.
    It reads the most recent Excel file from a specified directory, loads from differents sheets, and offer 
    various methode to filter and save data

    Attributes :
    path (str) : The directory path where Excel files are located.
    filename (str) : The past of the latest Excel file found in the directory.
    data_plate (DataFrame) : Data loaded from the "Plates" sheet in the Excel file.
    data_frame (DataFrame) : Data loaded from the "Vials_Caps" sheet in the Excel fil.
    """
    def __init__(self, path):
        """
        Initialize the Data class with a directory path.

        Parameter:
        path (str) : The directory ath where Excel file are located.
        """
        self.path = path
        self.filename = self.get_latest_file()
        self.data_plate, self.data_vial = self.get_data()

    def get_latest_file(self) : 
        """
        Finds the most recently modified Excel file in the specified directory.
        
        Returns:
        str: Path to the most recently modified `.xlsx` file, or None if no `.xlsx` files are found.
        """

        files = [os.path.join(self.path, f) for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        files = [f for f in files if f.endswith(".xlsx")]

        if not files : 
            return None
        
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    def get_data(self) : 
        """
        Reads data from the two sheets: "Plates" and "Vials_Caps".
        
        Returns:
        tuple: A tuple containing two DataFrames: data_plates and data_vial_caps.
        """

        data_plates = None
        data_vial_caps = None

        file = self.get_latest_file()

        sheets = pd.read_excel(file, sheet_name=None)
    
        for sheet_name, data in sheets.items() : 
            if sheet_name == SECOND_SHEET_NAME : 
                data_vial_caps = pd.read_excel(file, sheet_name=sheet_name)
            else :
                data_plates = pd.read_excel(file, sheet_name=sheet_name)

        return data_plates, data_vial_caps
    
    def get_filtered_data(self, data_type, filters) :
        
        """
        Filters data based on the specified data type and filter criteria.
        
        Parameters:
        data_type (str): The type of data to filter, either "plate" or "vial".
        filters (dict): A dictionary of column names and values to filter by.
        
        Returns:
        DataFrame: A filtered DataFrame based on the specified criteria.
        """

        filtered_df = self.data_plate if data_type == "plate" else self.data_vial if data_type == "vial" else None
        for key, value in filters.items() : 
            filtered_df = filtered_df[filtered_df[key] == value]

        return filtered_df

    def get_df(self, sheet) : 
        if sheet == "vial" :
            return self.data_vial
        elif sheet == "plate" :
            return self.data_plate
        else :
            return None

    def print_data(self) : 
        print(f"Data plate : \n {self.data_plate}")
        print(f"Data vial : \n {self.data_vial}")