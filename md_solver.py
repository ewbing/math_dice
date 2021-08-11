# Solve Math Dice Configurations
# Skye Rhomberg

import itertools as it
import md_parser as mp
import pickle as pkl
import sys
import subprocess
import os

# Binary (PEMDAS) ops
pemdas_ops = ['+','-','*','/','^']
# Factorial and Termial
unary_ops = ['!','?']
# Amount by which each operator/operand changes stack size
op_change = {'+':-1,'-':-1,'*':-1,'/':-1,'^':-1,'!':0,'?':0}
op_change.update({d:1 for d in range(1,7)})
# Valid Black Dice Answers: 11-16, 21-16, ..., 61-66
valid_ans = sum([[10*(i + 1) + j + 1 for j in range(6)] for i in range(6)],[])

#########################################################################################
# Generate Valid Expressions

def gen_valid_exprs(w_dice,n_unary=0):
    '''
    Generate All Valid Expressions
    For a given configuration of the dice
    For now, only use the PEMDAS operators
    Input:
    w_dice: 5-tuple of int. given white dice configuration
    n_unary: int. number of unary operators (!,?) allowable
    Output:
    generator of str. valid postfix expressions using each white die exactly once
    '''
    yield from _gen_expr('',[d for d in w_dice],n_unary,0)

def _next_valid(dice_left,stack_size,n_unary=0):
    '''
    Generate all candidates for next token
    Can be any valid digit or an operator if there are enough operands on stack
    Input:
    dice_left: list of int. remaining unused white dice
    stack_size: int. simulated size of calc stack
    n_unary: int. number of unary operators (!,?) allowable
    Output:
    list of ints or str. possible next tokens
    '''
    # Discount duplicates in dice_left
    # include binary ops if there are 2 operands on stack
    # include unary ops if there is 1 operand on stack and n_unary > 0
    return list(set(dice_left))+pemdas_ops*(stack_size>1)+unary_ops*(stack_size*n_unary>0)

def _rm_die(dice_left,n):
    '''
    Remove one instance of n from dice_left if it's there
    Return a copy
    '''
    return [d for d in dice_left if d != n] + [n] * (dice_left.count(n) - 1)

def _gen_expr(expr,dice_left,n_unary,stack_size):
    '''
    Recursively generate valid expression given partial expression
    and add it to list of valid expressions
    Input:
    expr: str. partially generated expression
    dice_left: list of int. white dice still unused
    n_unary: int. number of unary operators (!,?) allowable
    stack_size: simulated calc stack size for expr
    generator of next recursion level of partial expressions
    '''
    # Base Case: All digits and unaries used and stack size 1, i.e. result calculated
    if not dice_left and not n_unary and stack_size == 1:
        yield expr
    # For each valid next token
    for t in _next_valid(dice_left,stack_size,n_unary):
        # If number, stack size goes up by one
        # If binary op, down by one
        # If unary op, stays the same
        s = op_change[t]
        # 1 if unary, 0 if not
        n = t in unary_ops
        # Recurse with new token
        yield from _gen_expr(expr+str(t),_rm_die(dice_left,t),n_unary-n,stack_size+s)

#########################################################################################
# Generate Valid Solutions

def gen_valid_solutions(w_dice,b_dice=None,n_unary=0,verbose=False):
    '''
    Generate and score valid math dice solutions for a given set of white dice
    Valid solutions evaluate to whole numbers reachable with the black dice,
    i.e. 11-16,21-26,...,61-66
    Input:
    w_dice: 5-tuple of int. white dice combination
    n_unary: int. number of unary operators (!,?) allowable
    verbose: bool. verbose mode
    Output:
    dict. total:[(expr1,score),(expr2,score)] --> list of ways to get each combination
    '''
    if verbose:
        sys.stdout.write(f'Solving {w_dice}... '+' '*(9+n_unary))
    sols = {}
    ans = b_dice if b_dice else valid_ans
    for expr in gen_valid_exprs(w_dice,n_unary):
        if verbose:
            sys.stdout.write('\b'*(9+n_unary)+expr)
        if type(res := mp.evaluate(expr,mode='postfix')) == int and res in ans:
            if res in sols:
                sols[res].append((expr,mp.score(expr)))
            else:
                sols[res] = [(expr,mp.score(expr))]
    if verbose:
        sys.stdout.write('\b'*(9+n_unary)+'Done'+' '*(n_unary+5)+'\n')
    return sols

#########################################################################################
# Store Results

def make_sols_db(db_name,ws=None,n_unary=0,verbose=False):
    '''
    Store scored solutions for all math dice configurations
    Directory Structure:
    data/
        11111/
            11/
                u0.p
                u1.p
                ... [n_unary]
            12/
            ... [results in valid_ans]
        11112/
        ... [w_dice]
    Input:
    db_name: str. name of data parent directory
    ws. list of tuples. white dice combinations to try. If none, defaults to all
    n_unary: int. number of unary operators (!,?) allowable
    '''
    # For every possible white dice combo
    for w_dice in it.combinations_with_replacement(range(1,7),5):
        # Make output dir
        dir_name = f'{db_name}/{"".join([str(w) for w in w_dice])}'
        subprocess.run(['mkdir','-p',dir_name])
        # If white dice specified in ws or ws not specified (i.e. run all)
        if not ws or w_dice in ws:
            b_dice = ws[w_dice] if type(ws) is dict else None
            vs = gen_valid_solutions(w_dice,b_dice,n_unary,verbose)
            if verbose:
                sys.stdout.write(f'u{n_unary} sols: ')
            # For all results reachable with given n_unary
            for res in vs:
                # Make parent directories if needed
                subprocess.run(['mkdir','-p',f'{dir_name}/{res}'])
                # Save data/w_dice/b_dice/uX.p file
                with open(f'{dir_name}/{res}/u{n_unary}.p','wb') as out:
                    if verbose:
                        sys.stdout.write(f'{res} ')
                    pkl.dump(vs[res],out)
            if verbose:
                print('')

#########################################################################################
# Analyze

def get_sols(w_dice,b_dice,db_name):
    '''
    Find All Solutions to given configuration from dbs
    Input:
    w_dice: 5-tuple of int. white dice combination
    b_dice: int. black dice total
    db_name: str. name of solution db directory
    Output: list. [(solution,score),(solution,score)]
    '''
    w = tuple(sorted(w_dice))
    s_dir = os.path.join(db_name,''.join([str(w) for w in w_dice]),str(b_dice))
    sols = []
    if os.path.isdir(s_dir):
        for f in os.listdir(s_dir):
            with open(os.path.join(s_dir,f),'rb') as u:
                sols.extend(pkl.load(u))
    return sols

def unsolvable(w_dice,db_name,max_unary=10):
    '''
    List unsolvable black dice totals for each white die configuration
    Input:
    w_dice: 5-tuple of int. white dice combination
    b_dice: int. black dice total
    db_name: str. name of solution db directory
    max_unary: int. max allowed number of unary ops (! or ?)
    Output: list of int. unsolvable black dice configs for given white dice config
    '''
    s_dir = lambda b: os.path.join(db_name,''.join([str(w) for w in w_dice]),str(b))
    w = tuple(sorted(w_dice))
    return [b_dice for b_dice in valid_ans if not\
            any(os.path.isfile(os.path.join(s_dir(b_dice),f'u{n}.p'))\
            for n in range(max_unary+1))]

def get_all_unsolvable(db_name,max_unary=10):
    '''
    List all unsolvable combinations of white and black dice from dbs
    Skips combos with no unsolvable
    Input:
    db_name: str. name of solution db directory
    max_unary: int. max allowed number of unary ops (! or ?)
    Output: dict. (white_dice):[unsolvable black dice]
    '''
    lm = _list_missing_sols(db_name,max_unary)
    return {tuple(map(int,w_dice)):lm[w_dice] for w_dice in lm if lm[w_dice]}

def _list_missing_sols(db_name,max_unary=10):
    '''
    Helper function for get_all_unsolvable: Includes empty lists where no sols missing
    Input:
    db_name: str. name of solution db directory
    max_unary: int. max allowed number of unary ops (! or ?)
    Output: dict. (white_dice):[unsolvable black dice]
    '''
    return {w_dice:unsolvable(tuple(map(int,w_dice)),db_name,max_unary)\
            for w_dice in os.listdir(db_name)}

def has_unsolvable(db_name,max_unary=10):
    '''
    List all white dice combinations that have unsolvable black dice with given max_unary
    Input:
    db_name: str. name of solution db directory
    max_unary: int. max allowed number of unary ops (! or ?)
    Output: list of tuples. white dice combos with some unsolvable black dice
    '''
    return [w_dice for w_dice in get_all_unsolvable(db_name,max_unary)]

#########################################################################################
# Main

if __name__ == '__main__':
    ws = None
    for i in range(7):
        make_sols_db('new_sols',ws,i,True)
        ws = get_all_unsolvable('new_sols')
