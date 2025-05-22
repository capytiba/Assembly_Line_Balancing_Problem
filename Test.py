from algorithm import engine, read_file, read_operations_file

if __name__ == '__main__':

    possible_stations = read_operations_file('possible_stations.txt')
    for i in possible_stations:
        print(len(i))

    print(len(possible_stations))