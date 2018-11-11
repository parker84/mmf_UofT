import pickle

flatten = lambda l: [item for sublist in l for item in sublist]

def load_pickle(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)