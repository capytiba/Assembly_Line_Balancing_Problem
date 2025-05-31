from typing import Any
import time

from algorithm import engine, read_file, read_operations_file

if __name__ == '__main__':
    k, num_op, graph, times = read_file('dados_marqueze_ponderado.txt')
    num_stations = 11
    fixed_operations = read_operations_file('fixed_operations.txt') # gets a matrix with the fixed operations and the assigned stations
    free_operations = read_operations_file('possible_stations.txt')
    # list_of_fixed = {sublist[0] for sublist in fixed_operations} # temporary list for all fixed operations
    # free_operations = [x for x in range(num_op) if x not in list_of_fixed]
    print(f"Fixed_operations: {fixed_operations}")
    # print(f"list_of_fixed: {list_of_fixed}")
    print(f"Free operations: {free_operations}")
    print(f"Size of free operations: {len(free_operations)}")
    print("----------")






    engine(k, num_op, graph, times, num_stations=num_stations,
           pop_size=5000, iterations=1000,
           perc_elitism=10 / 100, perc_mat=0.2, sel_type='rank', cross_type='UX',
           mutation_rate=0.5, mut_type='random',
           fixed_operations=fixed_operations, free_operations=free_operations)



    """
    start = time.time()
    counter = 0
    for pop_size in [1000]: #, 4000, 8000]: # 4
        for perc_elitism in [0.01, 0.02]: #, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]: # 10
            for perc_mat in [0.1, 0.2]:#, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]: # 10
                for sel_type in ['roulette', 'rank', 'tournament']: # 3
                    for mutation_rate in [0.01, 0.025]:#, 0.04, 0.05, 0.06, 0.075, 0.09, 0.1, 0.12, 0.14, 0.17, 0.2, 0.35, 0.5, 0.75, 1.0]: # 16
                        for cross_type in ['SP', 'DP', 'UX']: # 3
                            engine(k, num_op, graph, times, num_stations=num_stations,
                                   pop_size=pop_size, iterations=1000,
                                   perc_elitism=perc_elitism, perc_mat=perc_mat, sel_type=sel_type, cross_type=cross_type,
                                   mutation_rate=mutation_rate, mut_type='random',
                                   fixed_operations=fixed_operations, free_operations=free_operations)
                            print(f"Calculation: {counter} - Time: {time.time() - start}")
                            start = time.time()
                            counter += 1
    """
