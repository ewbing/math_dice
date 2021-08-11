# Math Dice Humanizer
# Sift lists of expressions and indentify equivalent ones
# Skye Rhomberg

import re
import md_parser as mp

#########################################################################################
# Parse-Tree Conversion

def to_tree(expr):
    '''
    Convert Infix Expression (normal-form parends) to parse-tree
    7*(6+3+(3!)) --> ['7','*',['6','+','3','+',['3','!']]]
    Input:
    expr. str. infix expression with "normal" parends from md_parser.to_infix()
    Output:
    list. parse-tree of expression
    '''
    # Replace ( with [ and ) with ],
    # Quote-comma everything that's not a [ or ] or comma: 5 --> "5",
    s = re.sub(r'([^,[\]])',r'"\1",',expr.replace('(','[').replace(')','],'))
    # List-wrap and eval to produce the nested lists
    return eval(f'[{s}]')

def to_expr(tree,mode='smart'):
    '''
    Convert parse-tree back to expression
    Input:
    tree: list. parse-tree where nested sublists are subtrees
    Output:
    str. infix expression from tree -- parends turned to "smart" mode
    '''
    return _expr(tree,mode)

def _parend(subexpr,mode):
    '''
    Appropriately parenthesize an expression of arbitrary length
    Input:
    subexpr: list of str. sub-expression e.g. ['1','+','3','+','6'] or ['(3*2)-1','?']
    Output:
    str. appropriately parenthesized combined sub-expression from list
    '''
    # Length 2: Unary operation 
    if len(subexpr) == 2:
        # First element is operand, second is operator, parenthesize returns 1-len list
        return mp.parenthesize([subexpr[0]],subexpr[1],mode)[0] + subexpr[1]
    # Length 3: Regular binary operation
    if len(subexpr) == 3:
        return subexpr[1].join(mp.parenthesize(subexpr[::2],subexpr[1],mode))
    # Longer: multiple binary exprs with same operator + or *
    return subexpr[1].join(mp.parenthesize_multi(subexpr[::2],subexpr[1],mode))

def _expr(subexpr,mode):
    '''
    Recursively build up expression from parse-tree
    Input:
    subexpr: str or list of str. piece of expression
    Output:
    str. expression from that part
    '''
    # Base Case: already a str
    if type(subexpr) is str:
        return subexpr
    return _parend([_expr(t,mode) for t in subexpr],mode)

#########################################################################################
# Normalization

def dist_div_sub(tree):
    '''
    Distribute subtractions and divisions as many times as possible
    '''
    # Replacements
    d = {'-':'+','/':'*'}
    # Base Case: Reached individual symbol
    if type(tree) is str:
        return tree
    # If we have a / or - and another of the same in the right subtree
    if len(tree) == 3 and tree[1] in d and type(tree[2]) is list and\
            len(tree[2]) == 3 and tree[2][1] == tree[1]:
        # Change the /- to *+ and flip order of right subtree and recurse
        return [dist_div_sub(t) for t in [tree[0],d[tree[1]],tree[2][::-1]]]
    # If we have a / whose right subtree is a ^ whose right subtree is a -
    if len(tree) == 3 and tree[1] == '/' and type(tree[2]) is list and\
            len(tree[2]) == 3 and tree[2][1] == '^' and\
            type(tree[2][2]) is list and len(tree[2][2]) == 3 and tree[2][2][1] == '-':
        # Change the / to a * and flip the operands around the the - and recurse
        return [dist_div_sub(t) for t in [tree[0],'*', tree[2][:2]+[tree[2][2][::-1]]]]
    # Otherwise, just recurse as-is
    return [dist_div_sub(t) for t in tree]

def sort_commute(tree):
    '''
    Sort operands in commuting operations (+*) as follows:
    - "Shorter" expressions (i.e. list length or 1 if singular) to left
    - Ties broken by lexicography
    '''
    # Flatten list of arbitrary depth
    flatten = lambda *n: (e for a in n\
        for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    # Base Case: Reached individual symbol
    if type(tree) is str:
        return tree
    # If we have a commutable group (all operations are + or *)
    # Note that we cannot get a mix of + and * because of the "normal" parends
    if all(t in '+*' for t in tree[1::2]):
        # Sort the operands from shortest to longest, fallback to lex order
        # Use flattened list -- longer list includes length of sub-lists
        # Recurse bottom-up
        return list(sum(zip(sorted([sort_commute(t) for t in tree[::2]],\
                key = lambda s: (len([i for i in flatten(s)]),[i for i in flatten(s)])),\
                tree[1::2]+['']), ()))[:-1]
    # Otherwise, just recurse
    return [sort_commute(t) for t in tree]

def normalize(expr):
    '''
    Convert a postfix expression to "normal form" infix
    Normal form:
    - Wherever possible, subtraction and division are distributed: 5-(3-4) --> 5+(4-3)
    - Addition and multiplication have terms sorted:
        - Smaller singular values to left
        - Unary ops and parended expressions to right
        - Ties broken by lexicography
    - "Implied" parends like 5+(4-3) skipped to re-obtain "smart" parends --> 5+4-3
    Input:
    expr: str. postfix expression
    Output:
    str. expression in normal form
    '''
    # Postfix --> Normal Mode Infix --> Parse-Tree
    ifx = to_tree(mp.to_infix(expr,mode='normal'))
    # Tree -- (Dist Div Sub) --> Tree --> Normal Mode Infix --> Tree
    dds = to_tree(to_expr(dist_div_sub(ifx),mode='normal'))
    # Tree -- (Sort Commute) --> Tree --> Smart Mode Infix
    return to_expr(sort_commute(dds),mode='smart')

#########################################################################################
# Solutions Organization

def humanize(sols):
    '''
    Organize solutions to a particular math dice problem
    Group based on normalization
    Input:
    sols: list of (postfix-expr,score) tuples
    Output:
    list of tup. ((normalized-infix,score),[smart-infix exprs which normalize to it])
    Tuples sorted by score and lex, smart-infix list sorted by lex
    '''
    # Output dict to be formatted
    h_sols = {}
    # For each postfix expression
    for (expr,score) in sols:
        # Normalize and score
        n = normalize(expr)
        s = mp.score(n)
        # If new solution
        if (n,s) not in h_sols:
            # If not already normalized
            if mp.to_infix(expr,mode='smart') != n:
                # Add to equivs
                h_sols[(n,s)] = [mp.to_infix(expr,mode='smart')]
            else:
                # Already in key
                h_sols[(n,s)] = []
        # If not equal to normalized
        elif mp.to_infix(expr,mode='smart') != n:
            # Add to equivs
            h_sols[(n,s)].append(mp.to_infix(expr,mode='smart'))
    # Remove duplicates caused by infix conversion, sort by lex order
    org_sols = {(n,s): sorted(list(set(h_sols[(n,s)]))) for (n,s) in h_sols}
    # Sort keys by score, then by lex of expr
    return sorted([(k,org_sols[k]) for k in org_sols],key=lambda x:(x[0][1],x[0][0]))

#########################################################################################
# Test Code

if __name__ == '__main__':
    ss = ['(1+1)?!??/((1+1)?!+1)','(1+(4-5)+4!+5*5)/4?','5/(((1^4)/3)/3)',\
            '(((1+1)?)*((((1+1)?)!)?))-1']
    for s in ss:
        print(s)
        expr = ''.join(mp.shunt(s))
        print(normalize(expr))

