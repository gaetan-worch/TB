from dotenv import load_dotenv
import os
import re

load_dotenv()

SIZE_TILE_WELLPLATE = eval(os.getenv("SIZE_TILE_WELLPLATE"))
EP_WALL_WELLPLATE = eval(os.getenv("EP_WALL_WELLPLATE"))
SIZE_OFFSET_PARADOX = eval(os.getenv("SIZE_OFFSET_PARADOX"))
SIZE_TILE_PARADOX = eval(os.getenv("SIZE_TILE_PARADOX"))

def convert_letter_to_int(letter) :
    """
    Converts a letter (A-Z) to its corresponding integer position (1-26).

    Args:
        letter (str): A single uppercase or lowercase letter.

    Returns:
        int: The integer representation of the letter (A -> 1, B -> 2, ..., Z -> 26).
    """
    return ord(letter.upper()) - ord('A') + 1

def calcul_position_vial(column, line) : 
    """
    Calculates the X and Y offsets for a vial position on the well plate.

    Args:
        column (int): The column index.
        line (int): The row index.

    Returns:
        tuple: A tuple (offset_x, offset_y) representing the calculated position in mm.
    """
    offset_x = SIZE_TILE_WELLPLATE/2 + (16-line)*(SIZE_TILE_WELLPLATE+EP_WALL_WELLPLATE+0.07*10**(-3))
    offset_y = SIZE_TILE_WELLPLATE/2 + (column-1)*(SIZE_TILE_WELLPLATE+EP_WALL_WELLPLATE)

    return offset_x, offset_y

def calcul_position_reactor(column, line) :
    """
    Calculates the X and Y offsets for a reactor position.

    Args:
        column (int): The column index.
        line (int): The row index.

    Returns:
        tuple: A tuple (offset_x, offset_y) representing the calculated position in mm.
    """
    offset_x = SIZE_OFFSET_PARADOX + (line-1)*SIZE_TILE_PARADOX
    offset_y = SIZE_OFFSET_PARADOX + (column-1)*SIZE_TILE_PARADOX

    return offset_x, offset_y

def split_letter_number(str) :
    """
    Splits a string containing a letter and a number into separate components.

    Args:
        value (str): A string containing one letter (A-Z) followed by a number.

    Returns:
        tuple: A tuple (letter, number) where:
            - letter (str): The extracted letter (A-Z).
            - number (int): The extracted number.

    Raises:
        Exception: If the string format is invalid (e.g., multiple letters or numbers).
    """
    str = str.upper()
    letters = re.findall("[A-Z]", str)
    number = re.findall("(\d+)", str)

    nbre_letters = len(letters)
    nbre_number = len(number)
    number = int(number[0])
    if nbre_letters > 1 or nbre_letters <= 0 :
        raise Exception("Error in letters position")
    if nbre_number > 1 or nbre_number <= 0 :
        raise Exception("Error in number position")
    return letters[0], number