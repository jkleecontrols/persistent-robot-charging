import cplex
import numpy as np



D = np.array([[5, 5, 5, 5, 5, 5, 10, 15, 20, 25],
              [20, 25, 20, 15, 25, 30, 30, 25, 30, 35]])

n = D.shape[1]
g = np.gcd.reduce(np.concatenate((D[0,:],D[1,:]),axis=None))
D = D / g
C = D[0, :]
T = (D.sum(axis=0))
t = np.lcm.reduce(T.astype(int))
nums=int(sum(T))
T_max=int(max(T))


A = np.zeros((n,nums+1))
p_matrix=[]
A_matrix=[]

k = 0


for i in range(n):
   A[i,k:k+int(T[i])]=np.ones(int(T[i]))    # equality
   k=k+int(T[i])
    
   p_i = np.zeros(int(T[i]))
   p_i[0:int(C[i])] = np.ones(int(C[i]))
   p_matrix.append(p_i)
   

   
A_bar = np.zeros((t,nums+1)) # inequality


for i in range(t):
    k=0
    for j in range(n):
        A_bar[i,k:k+int(T[j])]=np.roll(p_matrix[j], shift=i, axis=0)
        k=k+int(T[j])
    A_bar[i,-1]=-1




b = np.ones(n)
b_bar = np.zeros(t)


lb = np.zeros(nums+1)
ub = np.ones(nums+1)
ub[-1]=np.inf


intcon = list(range(nums+1))
c=np.zeros((nums+1))
c[-1]=1


# Solve the ILP problem
prob = cplex.Cplex()

       # Set the objective function
prob.objective.set_sense(prob.objective.sense.minimize)
prob.variables.add(obj=c, lb=lb, ub=ub, types='I'*len(c), names=[f'x{i}' for i in range(1, len(c) + 1)])

       # Add constraints
for i in range(len(b)):
           prob.linear_constraints.add(
               lin_expr=[cplex.SparsePair(ind=list(range(len(c))), val=A[i])],
               senses=['E'],
               rhs=[b[i]]
           )
temp = np.zeros((1,nums+1))          
for i in range(len(b_bar)):
           k=0
           for j in range(n):
               temp[0,k:k+int(T[j])]=np.roll(p_matrix[j], shift=i, axis=0)
               k=k+int(T[j])
           temp[0,-1]=-1
           prob.linear_constraints.add(
               lin_expr=[cplex.SparsePair(ind=list(range(len(c))), val=temp[0])],
               senses=['L'],
               rhs=[b_bar[i]]
           )

       # Set integer variables
prob.variables.set_types([(i, 'I') for i in intcon])

       # Solve the problem
prob.solve()

       # Get the results
x = prob.solution.get_values()
fval = prob.solution.get_objective_value()
status = prob.solution.get_status()

print(f'Optimal Objective Value: {fval}')
print(f'Solution Status: {status}')

