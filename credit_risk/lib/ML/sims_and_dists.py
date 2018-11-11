import numpy as np


def get_cosine_and_dot_feats(vector, matrix):
    """
    return 2 vectors, one w cosine sims and other w dot products
    between vector and every row in matrix
    :param vector: mx1 np array
    :param matrix: nxm np matrix
    :return:
    """
    dot_query_docs = np.matmul(matrix, vector)
    l2_norms = np.linalg.norm(np.append([vector], matrix, axis=0), axis=1)
    cosine_sims = dot_query_docs * ( 1 /(l2_norms[1: ] *l2_norms[0]))
    return cosine_sims, dot_query_docs


def get_distance_matrix(df, distance_measure, feat_col_ix=1):
    """
    return a distance matrix between every row of df
    Note: could probably be made faster w matrix algebra
    ass:
    - each row of df is an observation
    - distance measure returns 2 vals, 1st is of interest
    :param df:
    :param distance_measure:
    :param feat_col_ix: all cols > this val are used in distance computation
    :return:
    """
    n = len(df)
    dist_matrix = np.zeros((n,n))
    for i in range(n):
        for j in range(j):
            si = df.iloc[i, feat_col_ix:]
            sj = df.iloc[j, feat_col_ix:]
            dist_matrix[i,j] = distance_measure(si, sj)[0]
    return dist_matrix


if __name__ == '__main__':
    import pdb; pdb.set_trace()
    v = np.zeros(10)
    m = np.append(np.zeros((5,10)), np.ones((5,10)), axis=0)
    cos, dot = get_cosine_and_dot_feats(v, m)
    print(cos)
    print(dot)