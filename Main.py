from typing import Any
import time

import numpy as np

from algorithm import engine, read_file, read_operations_file

if __name__ == '__main__':
    k, num_op, graph, times = read_file('dados_marqueze_ponderado.txt')
    num_stations = 11
    fixed_operations = read_operations_file('fixed_operations.txt') # gets a matrix with the fixed operations and the assigned stations
    free_operations = read_operations_file('possible_stations.txt')
    print(f"Fixed_operations: {fixed_operations}")
    # print(f"list_of_fixed: {list_of_fixed}")
    print(f"Free operations: {free_operations}")
    print(f"Size of free operations: {len(free_operations)}")
    print("----------")





    """
    engine(k, num_op, graph, times, num_stations=num_stations,
           pop_size=5000, iterations=1000,
           perc_elitism=10 / 100, perc_mat=0.2, sel_type='rank', cross_type='UX',
           mutation_rate=0.5, mut_type='random',
           fixed_operations=fixed_operations, free_operations=free_operations)



    """
    start_all = time.time()
    start = time.time()
    counter = 0
    while True:
        for pop_size in [4000]: #, 4000, 8000]: # 4
            for perc_elitism in [0.05]: #, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30]: # 10
                for perc_mat in [0.05, 0.1, 0.15, 0.2]: #np.arange(0.05, 0.55, 0.05):  #, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]: # 10
                    for sel_type in ['tournament']: # 3 'roulette', 'rank',
                        for mutation_rate in np.arange(0.05, 1.05, 0.05):#, 0.04, 0.05, 0.06, 0.075, 0.09, 0.1, 0.12, 0.14, 0.17, 0.2, 0.35, 0.5, 0.75, 1.0]: # 16
                            for cross_type in ['UX']: # 3 'SP', 'DP',
                                engine(k, num_op, graph, times, num_stations=num_stations,
                                       pop_size=pop_size, iterations=1000,
                                       perc_elitism=perc_elitism, perc_mat=float(perc_mat), sel_type=sel_type, cross_type=cross_type,
                                       mutation_rate=float(mutation_rate), mut_type='random',
                                       fixed_operations=fixed_operations, free_operations=free_operations)
                                print(f"Calculation: {counter} - Time: {time.time() - start} - Time taken: {time.time() - start_all}")
                                start = time.time()
                                counter += 1
        if time.time() - start_all > 23000:
            break

    print(f"Total time: {time.time() - start_all}")

