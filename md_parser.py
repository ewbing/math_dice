# Math Dice Parser
# Natural Numbers, +, -, *, /, !, ?
# Skye Rhomberg

import re
import math

#########################################################################################
# Operator Definitions

operators = '+-*/^!?'
# Operator Associativity
associativity = {'+':'LR','-':'L','*':'LR','/':'L','^':'R','!':'L','?':'L'}
# Operator Precedence
precedence = {'+':0,'-':0,'*':1,'/':1,'^':2,'!':3,'?':3}
# For infix calculation, digits need high precedence
infix_precedence = {**precedence, **{str(i+1):999 for i in range(6)}}
# Number of operands
n_operands = {'+':2,'-':2,'*':2,'/':2,'^':2,'!':1,'?':1}
# Calculation
# Factorial : n! = n * (n-1) * ... * 1 
fact = {n:math.factorial(n) for n in range(10)}
# Termial : n? = n + n-1 + ... + 1
term = lambda n: (n+1)*(n/2) if n == int(n) and n>=0 else 1/0 
# Operator Dictionary
ops = {}
# Operation Evaluation
op_calc = {'+':'ops[0]+ops[1]','-':'ops[0]-ops[1]','*':'ops[0]*ops[1]','/':'ops[0]/ops[1]',
        '^':'math.pow(ops[0],ops[1])','!':'fact[ops[0]]','?':'term(ops[0])'}
# Pre-compute calculation lambdas for speed increase
calc = {t:eval('lambda: '+op_calc[t]) for t in op_calc}
# Infix String
infix = {'+':'{0}+{1}','-':'{0}-{1}','*':'{0}*{1}','/':'{0}/{1}',
        '^':'{0}^{1}','!':'{0}!','?':'{0}?'}

#########################################################################################
# Scoring

def score(expr):
    '''
    Return the score of an expression
    Scored on elegance: ^, !, ? are inelegant and carry a per-use penalty
    Input:
    expr: str. INFIX valid math-dice expression
    Output:
    int. total of the penalties on the expression
    '''
    # "Inelegant" operations carry a penalty
    penalties = {'^':2,'!':5,'?':11}
    # Score an expression by summing its penalties
    return sum([penalties[t] if t in penalties else 0 for t in expr])

#########################################################################################
# Tokenizer

# A token is multiple digits or anything that's not a digit or a space
token = re.compile('(\d+|[^ 0-9])')
# Tokenize function splits input string into tokens
tokenize = lambda s: re.findall(token,s)

#########################################################################################
# Evaluator

def eval_infix(expr):
    '''
    Evaluate a given math expression
    Input:
    expr: string. the math expression input
    Output:
    int. value of expression

    Valid sentences use natural numbers and +-*/^!?()
    Infix notation, spaces are ignored
    ! is factorial, ? is termial, i.e. triangle numbers [n? = n+(n-1)?]
    '''
    # Evaluate the postfix tokenized input
    try:
        postfix = shunt(tokenize(expr))
    except AssertionError as bad_shunt:
        return bad_shunt
    return stack_calc(postfix)

def evaluate(expr,mode='infix'):
    '''
    Safely Evaluate a given math expression
    Catch all possible exceptions and return error msgs
    Input:
    expr: string. the math expression input
    Output:
    int. value of expression

    Valid sentences use natural numbers and +-*/^!?()
    Infix notation, spaces are ignored
    ! is factorial, ? is termial, i.e. triangle numbers [n? = n+(n-1)?]
    '''
    try:
        if mode == 'infix':
            return eval_infix(expr)
        elif mode == 'postfix':
            return stack_calc(expr)
        else:
            print('Invalid Mode')
            exit()
    # Assertion Error from stack_calc: Invalid Expression
    except AssertionError as a_msg:
        return a_msg
    # Dividing by zero, also raised by termial of non-int
    except ZeroDivisionError:
        return 'Zero Division or Bad Termial'
    # Intermediate Calculation too large
    except OverflowError:
        return 'Overflow'
    # Value Error from a few places, e.g. decimal termials
    except ValueError as v_msg:
        return v_msg
    # Factorial or termial of decimal
    except TypeError:
        return 'TypeError'
    # Calculate factorial larger than 10
    except KeyError:
        return 'Bad Factorial'
    # Diving by a small float causes inf value
    except NameError:
        return 'Inf Division'

def stack_calc(expr,save_stack=False):
    '''
    Evaluate a given math expression
    Input:
    expr: string. the math expression input
    save_stack: bool. if true, save everything pushed onto stack
    Output:
    int. value of expression

    Valid sentences use natural numbers and +-*/^!?
    POSTFIX notation, no spaces allowed
    ! is factorial, ? is termial, i.e. triangle numbers [n? = n+(n-1)?]
    '''
    # Calculation Stack
    stack = []
    # Record of Intermediate Positions
    record = []
    for t in expr:
        # If t is a number, push it
        if t.isdigit():
            stack.append(int(t))
            if save_stack:
                record.append(int(t))
        # Else t is an operator
        else:
            # Make sure operator has enough operands
            assert len(stack) >= n_operands[t], 'Invalid Expression'
            # Pop appropriate number of operands off stack
            curr_ops = [stack.pop() for i in range(n_operands[t])][::-1]
            for i,o in enumerate(curr_ops):
                ops[i] = o
            # ops.update({i:stack.pop(-1*(i+1)) for i in range(n_operands[t])})
            # Evaluate operation and push back on stack
            stack.append(calc[t]())
            if save_stack:
                record.append(calc[t]())
    # At end of calculation, stack must have one element: the result
    assert len(stack) == 1, 'Invalid Expression'
    # Make sure no bad division has been done
    assert stack[0] == int(stack[0]), f'Non-Int Result ({stack[0]})'
    if save_stack:
        return int(stack[0]),record
    return int(stack[0])

#########################################################################################
# Postfix to Infix Conversion

def to_infix(expr,mode='smart'):
    '''
    Convert a given math expression from postfix to infix
    Input:
    expr: string. the math expression input
    mode: str. parenthesizing mode - see functions below
    Output:
    str. expression as infix

    Valid sentences use natural numbers and +-*/^!?
    POSTFIX notation, no spaces allowed
    ! is factorial, ? is termial, i.e. triangle numbers [n? = n+(n-1)?]
    '''
    # Calculation Stack
    stack = []
    for t in expr:
        # If t is a number, push it
        if t.isdigit():
            stack.append(t)
        # Else t is an operator
        else:
            # Make sure operator has enough operands
            assert len(stack) >= n_operands[t], 'Invalid Expression'
            # Pop appropriate number of operands off stack
            curr_ops = [stack.pop() for i in range(n_operands[t])][::-1]
            # Format new expression and push back on stack
            stack.append(infix[t].format(*parenthesize(curr_ops,t,mode)))
    # At end of calculation, stack must have one element: the result
    assert len(stack) == 1, 'Invalid Expression'
    # In full mode, enclose whole expression in parends
    return f'({stack[0]})' if mode == 'full' else stack[0]

def parenthesize(operands,operator,mode='smart'):
    '''
    Input:
    operands: list of str. operands for operator (could already be expressions)
    operator: str. +-*/^!?
    mode: str. which parend algorithm (see functions below)
    Output:
    list of str. operands appropriately parenthesized
    '''
    assert mode in ['smart','full','normal'], 'Invalid Mode'
    return eval(f'parenthesize_{mode}(operands,operator)')

def parenthesize_multi(operands,operator,mode='smart'):
    assert mode in ['smart','normal'], 'Invalid Mode'
    return eval(f'parenthesize_{mode}_multi(operands,operator)')

def parenthesize_smart(operands,operator):
    '''
    Smart parends - only parenthesize when needed
    '''
    # Test if string has balanced parentheses
    balanced = lambda s: s.count('(') == s.count(')')
    # Remove all parends and expressions inside parends, get precedence of remaining
    rm_parends = lambda s: [t for (i,t) in enumerate(s)\
            if balanced(s[:i+1]) and t not in '()']
    # Take minimum of precedence list, returning high precedence if empty
    am = lambda s: min(rm_parends(s),key=lambda t: infix_precedence[t])\
            if rm_parends(s) else None
    m = lambda s: infix_precedence[am(s)] if am(s) else 999
    # Expression needs to be in parends if...
    # (a) its min unparenthesized precedence is less than operator precedence - OR -
    # (b) its MUP equals operator precedence AND 
    #   (1) its MUO equals operator but it lacks the correct associativity OR
    #   (2) its MUO doesn't equal operator and operator lacks correct associativity
    p = lambda i,o: m(o) < infix_precedence[operator] or\
            m(o) == infix_precedence[operator] and\
            (am(o) == operator and 'LR'[i] not in associativity[am(o)] or\
            am(o) != operator and 'LR'[i] not in associativity[operator])
    return [f'({o})' if p(i,o) else o for i,o in enumerate(operands)]

def parenthesize_smart_multi(operands,operator):
    '''
    Smart parends for longer exprs of all + or all * for normalizer
    '''
    # Test if string has balanced parentheses
    balanced = lambda s: s.count('(') == s.count(')')
    # Remove all parends and expressions inside parends, get precedence of remaining
    rm_parends = lambda s: [t for (i,t) in enumerate(s)\
            if balanced(s[:i+1]) and t not in '()']
    # Take minimum of precedence list, returning high precedence if empty
    am = lambda s: min(rm_parends(s),key=lambda t: infix_precedence[t])\
            if rm_parends(s) else None
    m = lambda s: infix_precedence[am(s)] if am(s) else 999
    # Expression needs to be in parends if
    # its min unparenthesized precedence is less than operator precedence
    # other cases will not occur as the only possible operators are +*
    return [f'({o})' if m(o) < infix_precedence[operator] else o for o in operands]

def parenthesize_normal(operands,operator):
    '''
    Parenthesize for normal form
    Always parenthesize except:
    - Unary ops or digits or other unary ops
    - Multiple +s or *s
    '''
    # Test if string has balanced parentheses
    balanced = lambda s: s.count('(') == s.count(')')
    # Remove all parends and expressions inside parends, and all digits and unary ops
    rm_pd = lambda s: [t for (i,t) in enumerate(s) if balanced(s[:i+1]) and t in '+-*/^!?']
    # Don't Parenthesize when 
    # rm_pdu is empty (only digits & unary ops or already in parends)
    # Or when all ops in operand as well as operator are the same an in + or *
    p = lambda o: not rm_pd(o) or operator in '+*' and all(t==operator for t in rm_pd(o))
    return [f'({o})' if not p(o) else o for o in operands]

def parenthesize_normal_multi(operands,operator):
    return parenthesize_normal(operands,operator)

def parenthesize_full(operands,operator):
    '''
    Full parends - every expression wrapped
    '''
    return [f'({o})' for o in operands]

#########################################################################################
# Shunting-Yard Algorithm

def shunt(tokens):
    '''
    Shunting-Yard Algorithm
    Convert infix to postfix
    Input:
    tokens: list. Infix tokens to be read
    Output:
    list. tokens in Postfix
    '''
    # output queue
    output = []
    # operator stack
    op_stack = []
    for t in tokens:
        # If t is a number
        if t.isdigit():
            # Put into output queue
            output.append(t)
        # If t is an operator
        elif t in operators:
            # While the top of the opstack is an operator and
            # it has higher precedence than t or the same and t is left-associative
            while op_stack and op_stack[0] in operators and\
                    (precedence[op_stack[0]]>precedence[t] or\
                    precedence[op_stack[0]] == precedence[t] and\
                    'L' in associativity[t]):
                # Pop operators into output queue
                output.append(op_stack.pop(0))
            # Push t onto opstack
            op_stack.insert(0,t)
        # If t is a left parend
        elif t == '(':
            # Push it onto opstack
            op_stack.insert(0,t)
        # If t is a right parend
        elif t == ')':
            # While top of opstack not a left parend
            while op_stack[0] != '(':
                # Make sure parends are balanced
                assert op_stack, 'unbalanced parends'
                # pop terms into output
                output.append(op_stack.pop(0))
            # Make sure we made it back to opening (
            assert op_stack[0] == '(', 'unbalanced parends'
            # Discard the left parend
            op_stack.pop(0)
        else:
            raise AssertionError(f'invalid token: {t}')
    # While opstack not empty
    while op_stack:
        # Make sure parends balanced
        assert op_stack[0] != '(', 'unbalanced parends'
        # Pop opstack into output
        output.append(op_stack.pop(0))
    # Output queue is now in postfix
    return output

#########################################################################################
# Main Code

if __name__ == '__main__':
    # Evaluate User Input Expressions, Return to exit
    print('Math Dice Parser: Press [Return] to Exit')
    while expr := input('Enter Expression: '):
        print(f'{expr} = {evaluate(expr,mode="infix")}')
        print(f'Score: {score(expr)}')
