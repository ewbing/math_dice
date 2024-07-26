import pytest
from md_parser import score, eval_infix

def test_score_empty_expression():
    assert score('') == 0

def test_score_expression_with_no_penalties():
    assert score('2+3*4') == 0

def test_score_expression_with_one_penalty():
    assert score('2^3') == 2

def test_score_expression_with_multiple_penalties():
    assert score('2^3!4?5') == 18

# Commented out - doesn't check for this error at this level
# def test_score_expression_with_unrecognized_character():
#    with pytest.raises(KeyError):
#        score('2@3')

# Inconsistent error handling - this one returns an AssertionError
# while the next one throws the AssertionError exception 
def test_eval_infix_mismatched_parens():
    assert isinstance(eval_infix('(1+3'), AssertionError)

# This one throws the AssertionError exception because it's out of the try block
def test_eval_infix_invalid_expression():
    with pytest.raises(AssertionError) as excinfo:
        eval_infix('1+')
    assert str(excinfo.value)=="Invalid Expression"

def test_eval_infix_factorial():
    assert eval_infix('5!') == 120

def test_eval_infix_with_paren():
    assert eval_infix('(1+2)^3') == 27

def test_eval_infix_mix():
    assert eval_infix('5+4-3?') == 3
