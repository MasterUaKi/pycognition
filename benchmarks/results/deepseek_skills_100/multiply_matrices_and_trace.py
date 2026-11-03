def multiply_matrices_and_trace(matrix_a, matrix_b):
    """
    Multiplies two square matrices and returns the product matrix and its trace.

    Args:
        matrix_a: list of lists of numbers (square matrix)
        matrix_b: list of lists of numbers (square matrix of same size as matrix_a)

    Returns:
        dict: {'product': list of lists of numbers, 'trace': number}
    """
    n = len(matrix_a)
    if n == 0:
        return {'product': [], 'trace': 0}
    if any(len(row) != n for row in matrix_a):
        raise ValueError('matrix_a must be a square matrix')
    if len(matrix_b) != n or any(len(row) != n for row in matrix_b):
        raise ValueError('matrix_b must be a square matrix of the same size as matrix_a')

    product = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += matrix_a[i][k] * matrix_b[k][j]
            product[i][j] = s

    trace = sum(product[i][i] for i in range(n))
    return {'product': product, 'trace': trace}
