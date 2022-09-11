# math_dice

The math dice are an obscure educational game meant to teach children arithmetic. The version pictured is nearly impossible to buy online, but boardgamegeek sells a toy called the [Number Jumbler](https://boardgamegeek.com/boardgame/18029/number-jumbler), which is the same except the white dice are colored.

To play the game, use each of the numbers on the white dice once and only once to write a mathematical expression which evaluates to the total on the black dice. Any mathematical expressions are allowable are in theory. In this repository, I consider the usual operations of addition, subtraction, multiplication, division, and exponents, as well as the factorial (`5! = 5*4*3*2*1`) and the "plus-torial" or "termial" (`5? = 5+4+3+2+1`).

This repo can generate all possible solutions to all the math dice puzzles using less than `n` factorials and/or termials. The zipped solutions database included goes up to `n=6`. At this depth, every puzzle has a solution except for one: `1 1 1 1 1` on the white dice and `51` on the black dice.

## Installation
Clone this repository,
```
git clone https://github.com/hadokat/math_dice.git
```
unpack the solutions database
```
tar -xzvf sols.tar.gz
```

This library requires `Python >3.9`. Update the shebang at the top of `./math_dice` according to your installation.
For example, if Python 3.9 is installed separately from an older Python 3.X:
```
#!/usr/bin/env python3.9
```
If installed as the only version of Python 3:
```
#!/usr/bin/env python3
```
If installed as the only (or defualt) version of Python:
```
#!/usr/bin/env python
```

## Usage

Play Game with Scoring:
```
math_dice game -sno
```

Analyze Solution:
```
math_dice analyze -soa WWWWW BB <solution>
```

Solve Configuration:
```
math_dice solve -q WWWWW BB
```

Use `./math_dice -h` for full options
Full solutions database can be created with:
```
./math_dice generate -uv <dir_name> 0 1 2 3 4 5 6
```
or can be extracted from the tar file. Generating sols takes a WHILE.

To play without ! or ?, generate a new db with
```
./math_dice generate -v <dir_name> 0
```
and use it with `./math_dice -C <dirname> ...` (this generation shouldn't take more than a half hour or so)

Normalization (identifying which solutions are semantically identical) is still in progress. Currently not caught:
- commutation of - with + and / with * w/o parends
- distribution of - into + in parends
- distribution of / into * in parends
- adding vs subtracting 0
- multiplying/dividing/exponentiating 1

Well-Caught:
- Commutation of + with +, * with *
- Distribution of / into /, - into - in parends
- Distribution of / into - thru ^
