import sys
import json
import argparse
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class ToeplitzExtractor:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)

    def _generate_toeplitz_matrix(self, n, m):
        total_bits = m + n - 1
        key = self.rng.integers(0, 2, size=total_bits)
        matrix = np.zeros((m, n), dtype=int)
        for i in range(m):
            for j in range(n):
                matrix[i, j] = key[n - 1 + i - j]
        return matrix

    def extract(self, input_bits, output_length):
        n = len(input_bits)
        m = output_length
        input_vec = np.array(input_bits).reshape(-1, 1)
        T = self._generate_toeplitz_matrix(n, m)
        output_vec = (T @ input_vec) % 2
        return output_vec.flatten().tolist()

def generate_quantum_entropy(n_bits):
    # Using shots to get multiple bits efficiently
    # To get n_bits, we run a 1-qubit circuit n_bits times or use multiple qubits.
    # For simplicity and maximum entropy, we'll use 1 qubit and n_bits shots.
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    
    simulator = AerSimulator()
    # We set memory=True to get individual bit results
    job = simulator.run(circuit, shots=n_bits, memory=True)
    result = job.result()
    memory = result.get_memory()
    
    # Convert '0'/'1' strings to integers
    raw_bits = [int(bit) for bit in memory]
    return raw_bits

def main():
    parser = argparse.ArgumentParser(description='Quantum Random Number Generator Core')
    parser.add_argument('--bits', type=int, default=128, help='Number of random bits to generate')
    parser.add_argument('--seed', type=int, default=None, help='Seed for the extractor')
    args = parser.parse_args()

    try:
        # 1. Generate Raw Quantum Entropy
        # We generate slightly more bits to allow for extraction
        raw_bits = generate_quantum_entropy(args.bits)
        
        # 2. Extract randomness using Toeplitz
        extractor = ToeplitzExtractor(seed=args.seed)
        final_bits = extractor.extract(raw_bits, args.bits)
        
        # 3. Convert bits to Hex for the API
        bits_str = "".join(map(str, final_bits))
        hex_val = hex(int(bits_str, 2))[2:]
        
        output = {
            "status": "success",
            "bits": args.bits,
            "hex": hex_val,
            "binary": bits_str
        }
        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
