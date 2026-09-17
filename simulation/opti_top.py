import numpy as np
import random
import matplotlib.pyplot as plt

# Parameters
num_nodes = 30
num_vehicles = 3
max_cost = 100
profit_per_node = 10
profits = [profit_per_node] * num_nodes  # 모든 노드의 이익은 동일
costs = np.random.randint(1, 10, size=(num_nodes, num_nodes))  # 각 노드간 비용은 1에서 9까지 랜덤
np.fill_diagonal(costs, 0)  # 자기 자신으로의 이동 비용은 0

# Create initial population of routes for each vehicle
def create_initial_population(size, num_nodes, num_vehicles):
    return [[random.sample(range(num_nodes), num_nodes) for _ in range(num_vehicles)] for _ in range(size)]

# Evaluate fitness of a solution
def evaluate_fitness(solution, profits, costs, max_cost, num_vehicles):
    total_profit = 0
    for vehicle_route in solution:
        vehicle_cost = 0
        for i in range(len(vehicle_route) - 1):
            vehicle_cost += costs[vehicle_route[i]][vehicle_route[i+1]]
            if vehicle_cost > max_cost:
                break
        else:
            total_profit += sum(profits[vehicle_route[i]] for i in range(len(vehicle_route)))
    return total_profit

# Genetic algorithm to find the best solution
def genetic_algorithm(profits, costs, max_cost, population_size, num_generations, mutation_rate, num_vehicles):
    population = create_initial_population(population_size, num_nodes, num_vehicles)
    fitness_history = []

    for generation in range(num_generations):
        population.sort(key=lambda x: -evaluate_fitness(x, profits, costs, max_cost, num_vehicles))
        fitness_history.append(evaluate_fitness(population[0], profits, costs, max_cost, num_vehicles))
        next_population = []
        for i in range(0, population_size, 2):
            p1, p2 = population[i], population[i+1]
            c1, c2 = crossover(p1, p2, num_vehicles)
            next_population.extend([mutate(c1, mutation_rate, num_nodes), mutate(c2, mutation_rate, num_nodes)])
        population = next_population

    best_solution = population[0]
    return best_solution, fitness_history

# Crossover operation
def crossover(parent1, parent2, num_vehicles):
    child1, child2 = [], []
    for i in range(num_vehicles):
        cp = random.randint(1, len(parent1[i]) - 2)
        child1.append(parent1[i][:cp] + [x for x in parent2[i] if x not in parent1[i][:cp]])
        child2.append(parent2[i][:cp] + [x for x in parent1[i] if x not in parent2[i][:cp]])
    return child1, child2

# Mutation operation
def mutate(route, mutation_rate, num_nodes):
    for r in route:
        if random.random() < mutation_rate:
            i, j = random.sample(range(num_nodes), 2)
            r[i], r[j] = r[j], r[i]
    return route

# Plot the routes of each vehicle
def plot_vehicle_routes(best_solution, num_vehicles, num_nodes):
    G = nx.Graph()
    for node in range(num_nodes):
        G.add_node(node)
    pos = nx.spring_layout(G, seed=42)  # Node layout
    colors = ['red', 'blue', 'green', 'cyan', 'magenta']  # Colors for each vehicle

    # Draw each vehicle's route
    for idx, route in enumerate(best_solution):
        path_edges = list(zip(route[:-1], route[1:]))
        nx.draw_networkx_nodes(G, pos, nodelist=route, node_color=colors[idx % len(colors)], label=f'Vehicle {idx+1}')
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color=colors[idx % len(colors)], width=2)

    plt.title('Vehicle Routes Visualization')
    plt.legend()
    plt.show()

# Run the genetic algorithm and plot the best solution
# Execute the genetic algorithm
best_solution, fitness_history = genetic_algorithm(profits, costs, max_cost, 10, 100, 0.1, num_vehicles)

# Plot the best solution routes
plot_vehicle_routes(best_solution, num_vehicles, num_nodes)