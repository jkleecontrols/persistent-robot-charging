import numpy as np
from gurobipy import Model, GRB, quicksum
import matplotlib.pyplot as plt

n = 100
np.random.seed(42)  # For reproducibility

coord = np.random.rand(n, 2) * [30, 15] + [0, 15]

def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))

c = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        c[i, j] = euclidean_distance(coord[i], coord[j])

k = 25
b = 90

m = Model()
x = m.addVars(n, n, vtype=GRB.BINARY, name="x")
u = m.addVars(n, lb=0, name="u")

m.setParam('TimeLimit', 1000)

# Constraints
for j in range(1, n):
    m.addConstr(quicksum(x[i, j] for i in range(n)) - x[j, j] == 1)
    m.addConstr(quicksum(x[j, i] for i in range(n)) - x[j, j] == 1)

m.addConstr(quicksum(x[i, 0] for i in range(n)) - x[0, 0] <= k)
m.addConstr(quicksum(x[0, i] for i in range(n)) - x[0, 0] <= k)

m.addConstr(quicksum(x[0, i] for i in range(n)) - quicksum(x[i, 0] for i in range(n)) == 0)

m.addConstr(u[0] == 0)
for i in range(n):
    for j in range(1, n):
        if i != j:
            m.addRange(u[j] - u[i] - c[i, j] * x[i, j], -90, 90)

for i in range(n):
    m.addConstr(u[i] + c[i, 0] <= b)

m.setObjective(quicksum(c[i, j] * x[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)
m.optimize()

def get_path(next, x):
    path = [1]
    while next != 1:
        path.append(next)
        for i in range(n):
            if round(x[next, i].X) == 1:
                next = i
                break
    path.append(1)
    return path

paths = []
for i in range(n):
    if round(x[0, i].X) == 1:
        paths.append(get_path(i, x))

x_coords = coord[:, 0]
y_coords = coord[:, 1]
plt.scatter(x_coords, y_coords, label="Points")
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Random Points")

for path in paths:
    for j in range(len(path) - 1):
        plt.plot([coord[path[j] - 1][0], coord[path[j + 1] - 1][0]],
                 [coord[path[j] - 1][1], coord[path[j + 1] - 1][1]], 'b-')

plt.show()
