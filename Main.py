from typing import Any

from algorithm import engine, read_file, read_fixed_op_file, read_operations_file

if __name__ == '__main__':
    k, num_op, graph, times = read_file('dados_marqueze.txt')
    num_stations = 11
    fixed_operations = read_fixed_op_file('fixed_operations.txt') # gets a matrix with the fixed operations and the assigned stations
    free_operations = read_operations_file('possible_stations.txt')
    # list_of_fixed = {sublist[0] for sublist in fixed_operations} # temporary list for all fixed operations
    # free_operations = [x for x in range(num_op) if x not in list_of_fixed]
    print(f"Fixed_operations: {fixed_operations}")
    # print(f"list_of_fixed: {list_of_fixed}")
    print(f"Free operations: {free_operations}")


    engine(k, num_op, graph, times, num_stations=num_stations,
           pop_size=1000, iterations=10000,
           perc_elitism=10 / 100, perc_mat=0.8, sel_type='roulette', cross_type='SP',
           mutation_rate=0.25, mut_type='random',
           fixed_operations=fixed_operations, free_operations=free_operations)
