def matrix_multiply_and_trace(matrix_a, matrix_b):
    """
    Computes the matrix product of two 2D matrices and returns the trace
    of the resulting product matrix.

    Args:
        matrix_a: list[list[float]] - 2D matrix A (m x n)
        matrix_b: list[list[float]] - 2D matrix B (n x p)

    Returns:
        dict with keys:
            'product': list[list[float]] - matrix product A x B (m x p)
            'trace': float - trace of the product matrix (sum of diagonal)

    Raises:
        ValueError: if matrices are empty, ragged, or dimensions are incompatible.
        TypeError: if inputs are not lists of lists of numbers.
    """
    # Validate types
    if not isinstance(matrix_a, list) or not isinstance(matrix_b, list):
        raise TypeError("Both matrix_a and matrix_b must be lists of lists.")
    if len(matrix_a) == 0 or len(matrix_b) == 0:
        raise ValueError("Matrices must not be empty.")

    for row in matrix_a:
        if not isinstance(row, list) or len(row) == 0:
            raise ValueError("matrix_a must be a non-empty 2D list.")
    for row in matrix_b:
        if not isinstance(row, list) or len(row) == 0:
            raise ValueError("matrix_b must be a non-empty 2D list.")

    # Check rectangularity
    n_cols_a = len(matrix_a[0])
    for row in matrix_a:
        if len(row) != n_cols_a:
            raise ValueError("matrix_a must be rectangular.")
    n_cols_b = len(matrix_b[0])
    for row in matrix_b:
        if len(row) != n_cols_b:
            raise ValueError("matrix_b must be rectangular.")

    # Check numeric entries
    for row in matrix_a:
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise TypeError("matrix_a entries must be numbers.")
    for row in matrix_b:
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise TypeError("matrix_b entries must be numbers.")

    # Dimension compatibility
    m = len(matrix_a)
    n = n_cols_a
    n_b = len(matrix_b)
    p = n_cols_b
    if n != n_b:
        raise ValueError(
            "Incompatible dimensions: matrix_a is %dx%d, matrix_b is %dx%d."
            % (m, n, n_b, p)
        )

    # Compute product
    product = [[0.0 for _ in range(p)] for _ in range(m)]
    for i in range(m):
        for j in range(p):
            s = 0.0
            for k in range(n):
                s += matrix_a[i][k] * matrix_b[k][j]
            product[i][j] = s

    # Compute trace (sum of diagonal elements of product)
    trace = 0.0
    for i in range(min(m, p)):
        trace += product[i][i]

    return {"product": product, "trace": trace}
