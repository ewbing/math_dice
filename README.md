# math_dice

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
