import numpy as np
import matplotlib.pyplot as plt

# Define the function to calculate the distribution of eigenvalues
def eigenvalue_distribution(alpha, beta, N, num_matrices):
    eigenvalues = np.zeros((num_matrices, N))
    for i in range(num_matrices):
        # Generate a random asymmetric matrix with Hermitian symmetry
        A = np.random.normal(0, 1, (N, N))
        A = (A + A.T.conj()) / 2
        # Calculate the eigenvalues
        eigvals = np.linalg.eigvalsh(A)
        # Calculate the distribution function
        V = alpha**2 * np.sum(eigvals**2) + (1 - alpha**2) * np.sum((np.subtract.outer(eigvals, eigvals))**beta)
        eigenvalues[i] = V
    # Flatten the eigenvalues array and plot the histogram
    eigenvalues = eigenvalues.flatten()
    plt.hist(eigenvalues, bins=50, density=True)
    plt.title(f"Eigenvalue distribution for alpha={alpha}, beta={beta}, N={N}, num_matrices={num_matrices}")
    plt.xlabel("Eigenvalues")
    plt.ylabel("Density")
    plt.show()

# Example usage
eigenvalue_distribution(alpha=0.01, beta=2, N=100, num_matrices=100)