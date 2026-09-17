from gurobipy import*
import numpy as np

D = np.array([
    [14, 14, 14, 14],  # charging
    [20, 20 ,20, 20]   # flying
])
m = 2  # number of charging pads


n = D.shape[1] # number of vehicles
g = np.gcd.reduce(np.concatenate((D[0, :], D[1, :]), axis=None)) # 5 최대공약수
D = D / g 
C = D[0, :]
T = D.sum(axis=0)
t = np.lcm.reduce(T.astype(int)) # 840 최소공배수
nums = int(sum(T)) # 71 총 운행시간 합계
T_max = int(max(T))

A = np.zeros((n, nums)) # 10 x 72
K = np.zeros((n, nums))
p_matrix = []
q_matrix = []

k = 0

for i in range(n):
    A[i, k:k + int(T[i])] = np.ones(int(T[i]))  # equality
    K[i, k:k + int(T[i])] = np.ones(int(T[i]))  # equality
    k = k + int(T[i])

    p_i = np.zeros(int(T[i]))
    q_i = np.ones(int(T[i]))
    
    p_i[0:int(C[i])] = np.ones(int(C[i]))
    q_i[0:int(C[i])] = np.zeros(int(C[i]))
    
    p_matrix.append(p_i)
    q_matrix.append(q_i)

A_bar = np.zeros((t, nums))  # inequality
K_bar = np.zeros((t, nums))

for i in range(t):
    k = 0
    for j in range(n):
        A_bar[i, k:k + int(T[j])] = np.roll(p_matrix[j], shift=i, axis=0)
        K_bar[i, k:k + int(T[j])] = np.roll(q_matrix[j], shift=i, axis=0)
        k = k + int(T[j])
    # A_bar[i, -1] = -1
    # K_bar[i, -1] = -1

b = np.ones(n) # vehicle 수만큼
b_bar = np.zeros(t) # 
B = np.zeros((len(T), nums), dtype=int)

start_idx = 0

for i, duration in enumerate(T):
    # Explicitly converting indices to integers
    start_idx_int = int(start_idx)
    end_idx_int = int(start_idx + duration)
    
    # Fill the appropriate columns with 1s for each task
    B[i, start_idx_int:end_idx_int] = 1
    
    # Update the start index for the next task, explicitly ensuring it's an integer
    start_idx += duration
    
lb = np.zeros(nums)
ub = np.ones(nums)
lbn = np.zeros(n)
ubn = np.ones(n)

intcon = list(range(nums))
c = np.zeros((nums))
# c[-1] = 1

# Create a new model
model = Model("mip")

# Define decision variables
r = model.addVars(nums, vtype=GRB.INTEGER, lb=lb, ub=ub, name="r")
w = model.addVars(n, vtype=GRB.BINARY, lb=lbn, ub=ubn, name="w") # w

objective = quicksum(K_bar[i, j] * r[j] for i in range(t) for j in range(nums))
model.setObjective(objective, GRB.MAXIMIZE)

# # Add constraints
# w = np.ones(n)
# w = [quicksum(r[j] for j in range(int(sum(T[:i])), int(sum(T[:i + 1])))) for i in range(n)]

for i in range(len(b)): #n
    model.addConstr(quicksum(B[i, j] * r[j] for j in range(len(c))) == w[i])
    
for i in range(len(b_bar)):
    model.addConstr(quicksum(A_bar[i, j] * r[j] for j in range(nums)) <= m) #, name=f"Constraint_{i}")

# Optimize model
model.optimize()
    
# Get results
if model.status == GRB.OPTIMAL:
    # Extracting decision variable values
    x_values = {v.varName: v.x for v in model.getVars()}  # Corrected to get values from all variables
    fval = model.objVal
    print(f'Optimal Objective Value (max flight time): {fval}')
    print("Decision Variables Values: ")
    for varName, value in x_values.items():
        print(f"{varName}: {value}")
else:
    # Adjusted to provide a descriptive status message in case of non-optimality
    status_description = {v: k for k, v in model.Status.items()}  # Reverse mapping for status
    print(f'Model could not be solved to optimality. Solution Status: {model.status} - {status_description[model.status]}')

