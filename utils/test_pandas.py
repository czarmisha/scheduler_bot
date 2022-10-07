# import pandas as pd
# import itertools

# index = list(itertools.product(["Ada", "Quinn", "Violet"], ["Comp", "Math", "Sci"]))
# headr = list(itertools.product(["Exams", "Labs"], ["I", "II"]))
# indx = pd.MultiIndex.from_tuples(index, names=["Student", "Course"])
# cols = pd.MultiIndex.from_tuples(headr)  # Notice these are un-named
# data = [[70 + x + y + (x * y) % 3 for x in range(4)] for y in range(9)]
# df = pd.DataFrame(data, indx, cols)

# print(df)