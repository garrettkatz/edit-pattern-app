import pandas as pd

problems = pd.DataFrame(
columns = ['name', 'seconds'],
data = [
    ("sumthree", 300), 
    ("inrange", 300), 
    ("fizzbuzz", 300), 
    ("factorial", 300), 
    ("divisors", 300), 
    ("arraysum", 300), 
    ("double", 300), 
    ("collatz", 300), 
    ("stringsort", 300), 
    ("validbracket", 450), 
    ("binomial", 300), 
    ("divisors2", 450), 
    ("itemsort", 450), 
    ("positionsort", 450), 
    ("minesweeper", 600), 
    ("tictactoe", 600), 
])

if __name__ == "__main__":

    print(problems)

