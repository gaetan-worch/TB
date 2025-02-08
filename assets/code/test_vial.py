import pytest
from apps.shared.models.vials import *

vial = Vials("a", 1, 0)

def test_generate_vial() :

    assert vial.id == 0
    assert vial.product == "a"
    assert vial.quantity == 1

def test_get_id() :
    assert vial.get_id() == vial.id

def test_get_product() :
    assert vial.get_product() == vial.product

def test_get_quantity() :
    assert vial.get_quantity() == vial.quantity

def test_raise_quantity() :
    with pytest.raises(ValueError) :
        Vials("a", -1, 0)

def test_raise_id() :
    with pytest.raises(ValueError) :
        Vials("a", 1, -1)

def test_print_vial(capsys) :
    vial.print_caracteristique()
    captured = capsys.readouterr()
    assert captured.out == "product : a qty : 1 id : 0\n"