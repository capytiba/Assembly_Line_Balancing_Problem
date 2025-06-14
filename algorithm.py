import copy
import math
from random import random
from classes import Individual
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import csv
import os

def gen_indv(cross_type, mut_type, num_stations, num_operations, fixed_operations, free_operations):
    # print(f"Length of fixed: {len(fixed_operations)}")
    #code = [randint(0, num_stations - 1) for i in range(num_operations)]
    code = [0] * num_operations
    for i in range(len(fixed_operations)):
        code[fixed_operations[i][0]] = fixed_operations[i][1]
    for i in range(len(free_operations)):
        code[free_operations[i][0]] = free_operations[i][randint(1, len(free_operations[i])-1)]

    #print(f"Code: {code}")
    return Individual(num_operations, num_stations, code, cross_type=cross_type, mut_type=mut_type)


def create_population(pop_size, cross_type, mut_type, num_stations, num_operations, fixed_operations, free_operations):
    """
    Creates the initial population.

    Args:
        free_operations: matrix of the free operations and their possible stations.
        fixed_operations: list of fixed operations
        pop_size (int): the size of the population
        cross_type (string): crossing technique
        mut_type (string): mutation technique
        num_stations (int): number of stations
        num_operations (int): number of operations

    Returns:
        (list(Individual)): initial population
    """
    pop = [gen_indv(cross_type, mut_type, num_stations, num_operations, fixed_operations, free_operations) for i in range(pop_size)]

    return pop


def rank_population(k, graph, times, pop, gen):
    """
    Return the sorted population.

    Args:
        k (float): time of the slowest operation
        graph (dict): precedence graph of the problem
        times (list(float)): list containing the time of each operation
        pop (list(Individual)): Population
        gen (int): current generation

    Returns:
        (list(Individual)): Sorted population
    """

    return sorted(pop, key=lambda x:x.calc_fitness(gen, graph, times, k=k*10, scalling_factor=0) if x.fitness == 0 else x.fitness, reverse=False)


def select_by_tournament_(population):

    i = randint(0, len(population) - 1)
    j = randint(0, len(population) - 1)

    return population[i] if (population[i].fitness > population[j].fitness)else population[j]


def select_by_tournament(population, num=2):

    return [select_by_tournament_(population) for i in range(num)]


def select_by_rank(population, num=2):

    total = len(population)*(1 + len(population))/2
    rank = [i/total for i in range(1, len(population) + 1)]
    return np.random.choice(a=population, size=num, p=rank)


def select_by_roulette(population, num=2):
    total = reduce(lambda x, y: x + y.fitness, population, 0)
    roulette = [indiv.fitness / total for indiv in population]

    return np.random.choice(a=population, size=num, p=roulette)


def engine(k, num_operations, graph, times, num_stations=10,
           pop_size=100, iterations=100,
           perc_elitism=0.1, perc_mat=0.1, sel_type='roulette', cross_type='SP',
           mutation_rate=0.05, mut_type='random',
           fixed_operations=None, free_operations=None
           ):
    """
    Performs the genetic algorithm

    Args:
        free_operations: a list of free operations
        fixed_operations: matrix of fixed operations
        k (float): Time of the slowest station
        num_operations (int): Number of operations
        graph (dict): Precedence graph of the problem
        times (list(float)): List containing the times of the stations
        num_stations (int): Number of stations
        pop_size (int): Number of individuals in each population
        iterations (int): Number of generations
        perc_elitism (float): Percentage of the best individuals of the current generation that will carry over the next
                              Default to 0.1
        perc_mat (float): Percentage of the best individuals of the current generation that will have a chance to be
                          selected as a parent. Default to 0.1
        sel_type (String): Selection method that will be used.
                           OPTIONS:
                                    - roulette (default)
                                    - tournament
                                    - rank
        cross_type (String): Crossover operator that will be used
                             OPTIONS :
                                    - SP -> Single point crossover (default)
                                    - DP -> Double point crossover
                                    - UX -> Uniform crossover
        mutation_rate (float): Mutation rate. Default to 0.05
        mut_type (String): Mutation operator
                           OPTIONS:
                                    - random -> Random mutation (gives a random value to a random element) (default)
                                    - heur -> Heuristic mutation
                                    - swap -> Swap mutation (select 2 elements and swaps them)
                                    - scramble -> scramble subset
                                    - inverse -> Inverse subset

    Returns:
        (Individual): Best individual-ç
        (list(float)): Fitness of the bests solutions for every generation. Useful for plotting
        (list(float)): Mean fitness of the population for every generation. Useful for plotting
    """

    if fixed_operations is None:
        fixed_operations = []
    population = rank_population(k, graph, times,
                                 create_population(pop_size, cross_type, mut_type, num_stations, num_operations, fixed_operations, free_operations),
                                 0)

    best = []
    mean = []

    select = eval('select_by_' + sel_type)

    # Initialize stagnation tracking
    best_fitness_so_far = float('inf')
    stagnation_counter = 0

    for i in range(iterations):

        best.append(population[0].fitness)
        mean.append(reduce(lambda x, y: x + y.fitness, population, 0)/pop_size)
        # Break after:
        if population[0].gen < i - 15:
            break

        # Elitism
        new_generation = population[:int(perc_elitism*pop_size)]

        # Selection
        the_chosen_ones = select(population[:int(pop_size * perc_mat)], num=(pop_size - int(perc_elitism*pop_size)))

        mut = 2
        # Crossover
        for j in range(0, len(the_chosen_ones), 2):

            if j == len(the_chosen_ones) - 1:
                new_generation.append(Individual(num_operations, num_stations, copy.deepcopy(the_chosen_ones[j].code),
                                                 cross_type=cross_type, mut_type=mut_type))
                mut = 1
            else:
                new_generation.extend(the_chosen_ones[j].crossover(the_chosen_ones[j+1]))

            # Mutation
            for indv in new_generation[-mut:]:
                if random() < mutation_rate:
                    if mut_type == 'heur':
                        indv.mutate(graph, free_operations)
                    else:
                        indv.mutate(free_operations)

        # Evaluation
        population = rank_population(k, graph, times, new_generation, i)
        all_station_times = population[0].get_station_time(times)
        all_operator_times = population[0].get_operator_time(times)
        #print(f"Gen {i}; Best Fitness: {population[0].fitness}; Cycle time: {max(all_operator_times)}; Max station time: {max(all_station_times)}")
        #print(f"Best individual: {population[0].code}")



    violations = population[0].calc_violations(graph, True)
    '''
    if violations > 0:
        print("SOLUCION NO VALIDA: ", population[0].calc_violations(graph, False))
    else:
        print("No violations")
    
    
    formatted_str = "[%s]" % ", ".join(f"{num+1:02d}" for num in population[0].code)
    #formatted_list = [f"{num+1:02d}" for num in population[0].code]
    print("Operation :                 [01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]")
    print(f"Code of the best solution : {formatted_str}")
    #print(f"Code of the best solution : {[i+1 for i in population[0].code]}")
    print(f"Best solution reached after {population[0].gen} generations.")
    print(f"Fitness of the best solution : {population[0].fitness}")
    '''
    all_station_times = population[0].get_station_time(times)
    all_operator_times = population[0].get_operator_time(times)

    '''
    print(f"Cycle time of the best solution: {max(all_operator_times)}")
    

    print(f"Station times: {[all_station_times]}")
    print(f"Operator times: {[all_operator_times]}")

    
    station = [0] * num_stations
    for i in population[0].code:
        station[population[0].code[i]] = i
    print(f"Stations: {station}")



    
    #Create a matrix with 11 empty rows (0-10)
    station = [[] for _ in range(num_stations)]

    # Populate the matrix with indices
    for index, number in enumerate(population[0].code):
        station[number].append(index+1)
    for i in range(num_stations):
        print(f"Station {i+1}: {station[i]}")
    '''


    # This is to save all the parameters and results in a csv file, so it can be checked later:

    # Define data as a dictionary (keys = CSV column headers)
    data = {
        'k': k,
        #'num_operations': num_operations,
        #'graph': graph,
        #'times': times,
        #'num_stations': num_stations,
        'pop_size': pop_size,
        'iterations': iterations,
        'perc_elitism': perc_elitism,
        'perc_mat': perc_mat,
        'sel_type': sel_type,
        'cross_type': cross_type,
        'mutation_rate': mutation_rate,
        'mut_type': mut_type,
        #'fixed_operations': fixed_operations,
        #'free_operations': free_operations,
        'best_solution_fitness': population[0].fitness,
        'solution_generation': population[0].gen,
        'cycle_time': max(all_operator_times),
        'station_times': all_station_times,
        'operator_times': all_operator_times,
        'violations': violations,
        'best_solution': population[0].code,
    }

    filename = 'resultados_all11.csv'

    # Check if the file exists and is not empty
    file_exists = os.path.isfile(filename)
    file_not_empty = file_exists and os.path.getsize(filename) > 0

    # Open the file in append mode
    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        # Write header only if the file is new or empty
        if not file_exists or not file_not_empty:
            writer.writeheader()

        # Append the data as a new row
        writer.writerow(data)

    return population[0], best, mean


def read_file(file_name):
    """
    Read file to get times and graph

    <Number of operations>
    <Time in operation 1>
    …
    <Time in operation n>
    <vertex op_i,op_j >
    …
    <vertex op_k,op_g >

    Args:
        file_name (string): file name

    Returns:
        (float): Time of slowest operation
        (int): Number of operations
        (dict): Precedence graph of the problem
        (list(float)): times of each operation
    """

    times = []
    graph = dict()

    with open(file_name) as fd:
        operations = int(fd.readline()[:-1])
        for k in range(operations):
            times.append(int(fd.readline()))
            graph[k] = []
        while True:
            line = fd.readline()
            if not line:
                break
            ij = line.split(',')
            graph[int(ij[0]) - 1].append(int(ij[1][:-1]) - 1)
    print(f"Graph: {graph}")
    return max(times), len(times), graph, times


def to_str(i):
    if i % 1000 == 0:
        return r'${ret}\times10^3$'.format(ret=str(int(i / 1000)))
    elif i % 100 == 0:
        return r'${ret}\times10^2$'.format(ret=str(int(i / 100)))
    return str(i)


def compare_crossover(k, num_operations, graph, times, num_stations=10):
    """
    Compares crossover type and plots them
    """

    bests = []
    f = lambda x: x < 3000

    plt.figure(figsize=(6.8, 10))
    plt.title("Crossover")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='blue', linestyle=':')
    plt.plot(best, label='Single Point', color='blue')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='DP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='red', linestyle=':')
    plt.plot(best, label='Double Point', color='red')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='UX',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='green', linestyle=':')
    plt.plot(best, label='Uniform', color='green')
    bests.append(best[-1])

    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])

    plt.legend(frameon=False, fontsize='large')
    plt.show()

# Doesn't work for David in his computer. best returns as an empty list.
def compare_selection(k, num_operations, graph, times, num_stations=10):
    """
    Compares selection type and plots them
    """

    bests = []
    f = lambda x: x < 3000

    plt.figure(figsize=(6.8, 10))
    plt.title("Selection")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')
    # print(f"Parameters of the best solution : {[i+1 for i in best]}")

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    if best:  # Check if list is not empty
        plt.plot(mean, color='blue', linestyle=':')
        plt.plot(best, label='Roulette', color='blue')
        bests.append(best[-1])
    else:
        print("Warning: No valid data for Roulette selection")
        bests.append(float('inf'))  # Append a default high value


    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='rank', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    if best:  # Check if list is not empty
        plt.plot(mean, color='red', linestyle=':')
        plt.plot(best, label='Rank', color='red')
        bests.append(best[-1])
    else:
        print("Warning: No valid data for Roulette selection")
        bests.append(float('inf'))  # Append a default high value

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='tournament', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    if best:  # Check if list is not empty
        plt.plot(mean, color='green', linestyle=':')
        plt.plot(best, label='Tournament', color='green')
        bests.append(best[-1])
    else:
        print("Warning: No valid data for Roulette selection")
        bests.append(float('inf'))  # Append a default high value

    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])

    plt.legend(frameon=False, fontsize='large')
    plt.show()


def compare_mutation(k, num_operations, graph, times, num_stations=10):
    """
    Compares mutation type and plots them
    """

    bests = []

    f = lambda x: x < 3000
    plt.figure(figsize=(6.8, 10))
    plt.title("Mutations types")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='blue', linestyle=':')
    plt.plot(best, label='Heur', color='blue')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='random')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='red', linestyle=':')
    plt.plot(best, label='Random', color='red')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='swap')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='green', linestyle=':')
    plt.plot(best, label='Swap', color='green')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='inversion')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='orange', linestyle=':')
    plt.plot(best, label='Inversion', color='orange')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=200,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='scramble')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='purple', linestyle=':')
    plt.plot(best, label='Scramble', color='purple')
    bests.append(best[-1])
    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])
    plt.legend(frameon=False, fontsize='large')
    plt.show()


def compare_perc_elitism(k, num_operations, graph, times, num_stations=10):
    """
    Compares mutation type and plots them
    """

    bests = []

    f = lambda x: x < 3000
    plt.figure(figsize=(6.8, 10))
    plt.title("Perc elitism")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=2 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='blue', linestyle=':')
    plt.plot(best, label='1%', color='blue')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='red', linestyle=':')
    plt.plot(best, label='5%', color='red')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=20 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='green', linestyle=':')
    plt.plot(best, label='10%', color='green')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=30 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='orange', linestyle=':')
    plt.plot(best, label='15%', color='orange')
    bests.append(best[-1])

    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])
    plt.legend(frameon=False, fontsize='large')
    plt.show()


def compare_perc_mat(k, num_operations, graph, times, num_stations=10):
    """
    Compares mutation type and plots them
    """

    bests = []

    f = lambda x: x < 3000
    plt.figure(figsize=(6.8, 10))
    plt.title("Perc mat")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.2, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='blue', linestyle=':')
    plt.plot(best, label='20%', color='blue')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.3, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='red', linestyle=':')
    plt.plot(best, label='30%', color='red')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.4, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='green', linestyle=':')
    plt.plot(best, label='40%', color='green')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='orange', linestyle=':')
    plt.plot(best, label='50%', color='orange')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.6, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='yellow', linestyle=':')
    plt.plot(best, label='60%', color='yellow')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.7, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.20, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='black', linestyle=':')
    plt.plot(best, label='70%', color='black')
    bests.append(best[-1])

    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])
    plt.legend(frameon=False, fontsize='large')
    plt.show()


def compare_mut_rate(k, num_operations, graph, times, num_stations=10):
    """
    Compares mutation type and plots them
    """

    bests = []

    f = lambda x: x < 3000
    plt.figure(figsize=(6.8, 10))
    plt.title("Mutation Rate")
    plt.xlabel('Generation', fontsize='large')
    plt.ylabel('Fitness', fontsize='large')

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.1, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='blue', linestyle=':')
    plt.plot(best, label='10%', color='blue')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.2, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='red', linestyle=':')
    plt.plot(best, label='20%', color='red')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.3, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='green', linestyle=':')
    plt.plot(best, label='30%', color='green')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.4, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='orange', linestyle=':')
    plt.plot(best, label='40%', color='orange')
    bests.append(best[-1])

    _, best, mean = engine(k, num_operations, graph, times, num_stations=num_stations,
                           pop_size=200, iterations=400,
                           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                           mutation_rate=0.5, mut_type='heur')

    best = list(filter(f, best))
    mean = list(filter(f, mean))
    plt.plot(mean, color='purple', linestyle=':')
    plt.plot(best, label='50%', color='purple')
    bests.append(best[-1])

    plt.yscale('log')
    ticks = sorted(bests + [1000, 3000])

    i = 0
    while i < len(ticks):
        if ticks[i - 1] < ticks[i] <= ticks[i - 1] + 5.5 * 10 ** int(math.log10(ticks[i - 1]) - 1):
            if not ticks[i - 1] in bests:
                del ticks[i - 1]
            else:
                del ticks[i]
        elif ticks[i] <= ticks[i - 1] <= ticks[i] + 5.5 * 10 ** int(math.log10(ticks[i]) - 1):
            if not ticks[i] in bests:
                del ticks[i]
            else:
                del ticks[i - 1]
        else:
            i += 1

    plt.yticks(ticks)
    plt.yticks(ticks, [to_str(i) for i in ticks])
    plt.legend(frameon=False, fontsize='large')
    plt.show()


def get_best_num_stations_effort(k, num_operations, graph, times, i=1, j=10):
    """
    Tries to find the optimal number of stations (in a given range). It also plots the effort. We define effort as the product
    of time and fitness.

    Args:
        k (float) : time of the slowest operation
        num_operations (int): Number of operations
        graph (dict): Precedence graph of the problem
        times (list(float)): List containing the times of the stations
        i (int): lower bound of the search range
        j (int): upper bound of the search range

    Returns:
        (int): Number of stations in which the fitness is minimize
        (float): Time of the best solution
        ([int]): Codification of the best solution
    """

    my_best = math.inf
    best_indv = None
    num_stations = 0
    bests = []

    for z in range(i,j):

        print('Number of stations: %d' % z)
        rel_best, _, _ = engine(k, num_operations, graph, times, num_stations=z,
                          pop_size=200, iterations=500,
                          perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
                          mutation_rate=0.2, mut_type='heur')
        bests.append(rel_best.fitness)

        if rel_best.fitness < my_best:
            my_best = rel_best.fitness
            num_stations = z
            best_indv = rel_best
        print()

    plt.figure(figsize=(6.8, 10))
    plt.xlabel('Number of stations', fontsize='large')
    plt.ylabel('Quality', fontsize='large')

    esfuerzo = [0] * (j-i)

    for k in range(i, j):
        esfuerzo[k - i] = bests[k - i] * k

    plt.plot([sum(times)] * (j-i + 1), label='effort upper bound', color='black')
    plt.plot(*zip(*[(i+1, esfuerzo[i]) for i in range(len(esfuerzo))]), label='effort', marker='o', color='red')
    plt.plot(*zip(*[(i+1, bests[i]) for i in range(len(bests))]), label='time', marker='o', color='blue')

    plt.xticks([i for i in range(i,j)])

    plt.legend(frameon=False, fontsize='large')

    plt.show()

    print('\n********************************************************************************\n')
    print('\n********************************************************************************\n')
    print('Number of stations: %d, time = %d' % (num_stations, my_best))
    print('Individue: ', best_indv)
    return num_stations, best_indv, my_best

"""
def read_fixed_op_file(file_path):
    matrix = []
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                values = stripped_line.split(',')
                row = [int(values[0])-1, int(values[1])-1]
                matrix.append(row)
    return matrix
"""

# David, please unify them. Done
def read_operations_file(file_path):
    matrix = []
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line:
                values = stripped_line.split(',')
                row = [int(v)-1 for v in values]
                matrix.append(row)
    return matrix