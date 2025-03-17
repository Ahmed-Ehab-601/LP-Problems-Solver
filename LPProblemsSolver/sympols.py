import sympy as sp

# Define symbols
x, y = sp.symbols('x y')

# Create a SymPy matrix with symbols
M = sp.Matrix([
    [1, x, 3],
    [4, y, 6],
    [7, 8, 9]
])

# Row index to search in
row_index = 0  # First row (0-based indexing)

# Known values of symbols
known_values = {x: 2, y: 5}  # Substitute x = 2, y = 5

# Extract the row
row = M.row(row_index)

# Substitute known values into the row
row_substituted = row.subs(known_values)
sp.pprint(row_substituted)

# # Find the minimum value in the row
# min_value = min(row_values)

# # Find the index of the minimum value
# min_index = row_values.index(min_value)

# print(f"Row after substitution: {row_substituted}")
# print(f"Minimum value in row {row_index}: {min_value}")
# print(f"Index of minimum value: {min_index}")