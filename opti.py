from gurobipy import *

def solve_charging_pads_minimization(charging_times, flying_times):
    num_drones = len(charging_times)
    m = Model("charging_pads_minimization")
    T = 840 #sum(charging_times) + sum(flying_times)

    # Decision variables
    p = m.addVars(num_drones, range(T), vtype=GRB.BINARY, name="p")
    r = m.addVars(T, num_drones, vtype=GRB.BINARY, name="r")
    z = m.addVar(vtype=GRB.BINARY, name="z")
    
    # Additional variable: Total charging pads
    total_charging_pads = m.addVar(vtype=GRB.INTEGER, name="total_charging_pads")

    # Objective function: minimize the number of charging pads
    m.setObjective(total_charging_pads, GRB.MINIMIZE)

    # Constraint: z = p * r
    m.addConstrs(z == p[i, t] * r[t, i] for t in range(T) for i in range(num_drones))

    # Constraint: when t = 0, p[0, t] * r[t, 0] = 1
    m.addConstr(p[i, 0] * r[0, i] == 1 for i in range(num_drones))

    # Constraint: sum of z from time 1 to T is smaller than m
    m.addConstr(z <= total_charging_pads)

    # Solve the model
    m.optimize()

    # Display the solution
    if m.status == GRB.OPTIMAL:
        print("Optimal charging pad allocation:")
        for t in range(T):
            if p[0, t].x > 0.5:
                print(f"Drone is charging at time {t}")
        print(f"Minimum charging pads required: {int(total_charging_pads.x)}")
    else:
        print("No optimal solution found.")

# Example charging and flying times
charging_times = [5, 5, 5, 5, 5, 5, 10, 15 ,20, 25]
flying_times = [20, 25, 20, 15, 25, 30, 30, 25, 30, 35]

# Solve the problem
solve_charging_pads_minimization(charging_times, flying_times)
