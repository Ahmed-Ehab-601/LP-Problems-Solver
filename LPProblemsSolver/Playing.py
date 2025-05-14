from sympy import Matrix, pprint
from SubscriptSuperscriptLists import SubscriptSuperscriptLists
print("hello")
varName = {0: "x1", 1: "x2"}
# # vars ={}
# # for key,value in varName.items():
# #     varName.pop(key)
# #     varName[key+1] = value

# print(varName)    
# print(varName[1])
# print(varName[0])
# table = Matrix([[1, 2], [3, 'c']])

# pprint(table)

# M = Matrix([
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ])

# pprint(M[1, :])  # Outputs the entire second row: Matrix([[4, 5, 6]])
# pprint(M[:, 2])  # Outputs the entire third column: Matrix([[3], [6], [9]])
# print(M[1, 2])  # Outputs the element at row 1, col 2: 6


# tableau = Matrix([
#     [1, -3, 'c', 0,  0,  0],  
#     [0,  1,  1, 1,  0,  8],  
#     [0,  2,  3, 0,  1, 12]
# ])

# pivot = tableau[0, 1]  # Pivot element (row 1, col 1)

# # Scale entire row without loop
# tableau[0, :] = tableau[0, :]/pivot

# for i in range(1, tableau.shape[0]):
#     tableau[i, :] = tableau[i, :] - tableau[i, 1] * tableau[0, :]

# pprint(tableau)

# vector = Matrix([1, 2, 3])
# print(vector)


subscribts = SubscriptSuperscriptLists()
x = "x₁"
print(subscribts.extract_subscript_number(x))

