# Code style guide

We use "lowerCamelCase" to name files, functions and variables and UpperCamelCase for classes.

To avoid confusion or misleading code structures we split out code into functions that should satisfy only one purpose.
This functions should have type hints and docstrings that descripes what the function is doing. If the type hints are not
clear enough about an variable that is goin in or coming out of an function, this variable should also be explained in the docstring.
Moreover that, the docstring should descripe if any exception is thrown and why.

We use four spaces in files ending with `.py` as indent and tabs for all other file types.

# Security

To not leverage security it is necessary to avoid reading out the URL parameters in javascript.
Otherwise, an attacker can set something like `?id=doSomethingEvil()` in the URL.