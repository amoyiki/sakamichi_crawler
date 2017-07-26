import os

def get_for_file(file):
    pool = []
    with open(file, 'r') as f:
        for line in f:
            pool.append(line)
    return pool
