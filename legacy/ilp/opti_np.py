from gurobipy import*
import numpy as np

D = np.array([[5, 5, 5, 5, 5, 5, 10, 15, 20, 25], # charging
              [20, 25, 20, 15, 25, 30, 30, 25, 30, 35]]) # flying

n = D.shape[1] #
g = np.gcd.reduce(np.concatenate((D[0, :], D[1, :]), axis=None)) # 5 최대공약수
D = D / g 
C = D[0, :]
T = D.sum(axis=0)
t = np.lcm.reduce(T.astype(int)) # 840 lcm 최소공배수
nums = int(sum(T)) # 총 운행시간 합계
T_max = int(max(T)) 

A = np.zeros((n, nums + 1)) # 10 x 72
p_matrix = []

k = 0

for i in range(n):
    A[i, k:k + int(T[i])] = np.ones(int(T[i]))  # equality
    k = k + int(T[i])

    p_i = np.zeros(int(T[i]))
    p_i[0:int(C[i])] = np.ones(int(C[i]))
    p_matrix.append(p_i)

A_bar = np.zeros((t, nums + 1))  # inequality

for i in range(t):
    k = 0
    for j in range(n):
        A_bar[i, k:k + int(T[j])] = np.roll(p_matrix[j], shift=i, axis=0)
        k = k + int(T[j])
    A_bar[i, -1] = -1

b = np.ones(n) # vehicle 수만큼
b_bar = np.zeros(t) # 

lb = np.zeros(nums + 1)
ub = np.ones(nums + 1)
ub[-1] = np.inf

intcon = list(range(nums + 1))
c = np.zeros((nums + 1))
c[-1] = 1

# Create a new model
model = Model("mip")

# Define decision variables
x = model.addVars(nums + 1, vtype=GRB.INTEGER, lb=lb, ub=ub, name="x")

# Set objective
model.setObjective(quicksum(c[i] * x[i] for i in range(len(c))), GRB.MINIMIZE)

# Add constraints
for i in range(len(b)): #n
    model.addConstr(quicksum(A[i, j] * x[j] for j in range(len(c))) == b[i])

for i in range(len(b_bar)): #t
    temp = np.zeros((1, nums + 1))
    k = 0
    for j in range(n): #b
        temp[0, k:k + int(T[j])] = np.roll(p_matrix[j], shift=i, axis=0)
        k = k + int(T[j])
    temp[0, -1] = -1
    model.addConstr(quicksum(temp[0, j] * x[j] for j in range(len(c))) <= b_bar[i])

# Optimize model
model.optimize()

# Get results
if model.status == GRB.OPTIMAL:
    x_values = model.getAttr('x', x)
    fval = model.objVal
    print(f'Optimal Objective Value: {fval}')
    print(f'Solution Status: {model.status}')
    print("x_values is: ", x_values)
else:
    print('Model could not be solved to optimality.')
