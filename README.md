# Credits to Guillermo Muñoz
Thanks Guillermo Muñoz, who coded the structure of the code!
I wrote more code to make it work for my case, but I wouldn't be abe to do so without everything Muñoz did before.

# Assembly Line Balancing Problem
Genetic algorithm for the Assembly Line Balancing Problem.

## Description
This is my the code for my TCC (Trabalho de Conclusão de Curso), or my Final Paper for my bachelor's degree in mechanical engineering (yes, it has nothing to do with mechanical engineer).
This is still being developed, but after I finish the paper I will try to make it more usable for whoever wants to try it or use it.

## The inicial contribution of Muñoz: 
The ALBP consists of assigning tasks to an ordered sequence of stations such that the precedence relations among the tasks are satisfied and some performance measure is optimized. There are some algorithms designed for this problem. The genetic algorithm approach is easy to program and can be easaly adapted for other problems such as the travelling salesman problem.
To find a better solution faster we defined an heuritic mutation operator. It assign a random station to a task that violates the precedence relations. 
We also include multiple selection methods (roulette, tournament, rank), mutation operators (random, swap, scramble, inverse), crossover operators (Double Point, Single Point, Uniform).
To compare the performance, we define comparations methods.

## My contribution:
- I added the option to say which stations an operation can go, including fixed ones.
- I also included operators, so now one operator can manage more than one station.
- I also included automatic operations, that are added in the total time of an station, but not in the total time of the operator (NEEDS TO BE CHANGED, BECAUSE IT'S HARDCODED NOW - I will work on this when possible).
- Population generation only places operations to possible stations.
- Random mutation now only mutate free operations to possible station. (other mutation types don't work).
- Added option to add operations that need to be in the same station.
- Crossover now places this operations in the same station (post crossover)
- Code with separeted operations that need to be together now count as violations.
-  

---

## Usage

How to run the algorithm

```python
from algorithm import engine, read_file

if __name__ == '__main__':
    k, num_op, graph, times = read_file('data75.txt')
    num_stations = 10

    engine(k, num_op, graph, times, num_stations=num_stations,
           pop_size=200, iterations=200,
           perc_elitism=10 / 200, perc_mat=0.5, sel_type='roulette', cross_type='SP',
           mutation_rate=0.20, mut_type='heur')
```

How to compare different selection methods

```python
from algorithm import compare_selection, read_file

# Comparaciones
if __name__ == '__main__':
    k, num_op, graph, times = read_file('data75.txt')
    stations = 10

    compare_selection(k, num_op, graph, times)
```
