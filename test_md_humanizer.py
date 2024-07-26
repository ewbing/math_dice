import re
import pytest
from md_humanizer import to_tree,to_expr,sort_commute
from md_parser import shunt

def test_to_tree_empty_expression():
    assert to_tree('') == []

def test_to_tree_single_number_expression():
    assert to_tree('5') == ['5']

def test_to_tree_simple_expression():
    assert to_tree('2+3') == ['2', '+', '3']

def test_to_tree_nested_expression():
    assert to_tree('(2+3)*4') == [['2', '+', '3'], '*', '4']

def test_to_tree_expression_with_operators_and_parentheses():
    assert to_tree('7*(6+3+(3!))') == ['7', '*', ['6', '+', '3', '+', ['3', '!']]]

# def test_to_expr_single_number():
#     assert to_expr(to_tree('1')) == '1'

# def test_to_expr_single_operator():
#     assert to_expr(to_tree('+')) == '+'

def test_to_expr_simple_expression():
    assert to_expr(to_tree('1+2')) == '1+2'

def test_to_expr_nested_expression():
    assert to_expr(to_tree('(2+3)*4')) == '(2+3)*4'

def test_to_expr_nested_expression_smart_mode():
    assert to_expr(to_tree('1+(2*3)'), mode='smart') == '1+2*3'

def test_sort_commute_single_symbol():
    # Test case: Single symbol
    tree = 'a'
    expected = 'a'
    assert sort_commute(tree) == expected

def test_sort_commute_commutable_group():
    # Test case: Commutable group
    tree = ['a', '+', 'b', '*', 'c', '+', 'd']
    expected = ['a', '+', 'b', '*', 'c', '+', 'd']
    assert sort_commute(tree) == expected

def test_sort_commute_nested():
    # Test case: Nested commutable group
    tree = ['a', '+', ['b', '-', 'c'], '+', 'd']
    expected = ['a',  '+', 'd', '+', ['b', '-', 'c']]
    assert sort_commute(tree) == expected

def test_sort_commute_double_nested():
    # Test case: Nested non-commutable group
    tree = [['a', '+', ['b', '-', 'c']], '+', 'd']
    expected = ['d', '+', ['a', '+', ['b', '-', 'c']]]
    assert sort_commute(tree) == expected

    import pytest
from md_humanizer import normalize

def test_normalize_and_shunt_1():
    input_expr = '(1+1)?!??/((1+1)?!+1)'
    expected_output = '(1+1)?!??/(1+(1+1)?!)'
    output = normalize(shunt(input_expr))
    assert output == expected_output

def test_normalize_and_shunt_2():
    input_expr = '(1+(4-5)+4!+5*5)/4?'
    expected_output = '(1+4!+4-5+5*5)/4?'
    output = normalize(shunt(input_expr))
    assert output == expected_output

def test_normalize_and_shunt_3():
    input_expr = '5/(((1^4)/3)/3)'
    expected_output = '3*5*3/1^4'
    output = normalize(shunt(input_expr))
    assert output == expected_output

def test_normalize_and_shunt_4():
    input_expr = '(((1+1)?)*((((1+1)?)!)?))-1'
    expected_output = '(1+1)?*(1+1)?!?-1'
    output = normalize(shunt(input_expr))
    assert output == expected_output

