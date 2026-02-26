import sys
import json
import argparse
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

class ToeplitzExtractor:
    """
    Proper entropy extractor. 
    Compresses N raw bits into M uniform bits (N > M).
    """
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)

    def _generate_toeplitz_matrix(self, n, m):
        # Matrix is M rows x N columns
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
        if n < m:
            raise ValueError(f"Input bits ({n}) must be greater than output bits ({m}) for extraction.")
            
        input_vec = np.array(input_bits).reshape(-1, 1)
        T = self._generate_toeplitz_matrix(n, m)
        
        # Matrix multiplication in GF(2)
        output_vec = (T @ input_vec) % 2
        return output_vec.flatten().tolist()

def generate_quantum_entropy(n_bits):
    circuit = QuantumCircuit(1, 1)
    circuit.h(0)
    circuit.measure(0, 0)
    
    simulator = AerSimulator()
    job = simulator.run(circuit, shots=n_bits, memory=True)
    result = job.result()
    memory = result.get_memory()
    
    return [int(bit) for bit in memory]

def main():
    parser = argparse.ArgumentParser(description='Quantum Random Number Generator Core')
    parser.add_argument('--bits', type=int, default=128, help='Number of final bits requested')
    parser.add_argument('--oversample', type=int, default=4, help='Oversampling factor (N = bits * factor)')
    parser.add_argument('--seed', type=int, default=None, help='Seed for the extractor matrix')
    args = parser.parse_args()

    try:
        m = args.bits
        n = m * args.oversample
        
        # Generate N raw bits (Higher entropy pool)
        raw_bits = generate_quantum_entropy(n)
        
        # Extract M bits (Compression improves entropy density)
        extractor = ToeplitzExtractor(seed=args.seed)
        final_bits = extractor.extract(raw_bits, m)
        
        bits_str = "".join(map(str, final_bits))

        # Ensure we handle the hex conversion for the exact bit length
        hex_val = hex(int(bits_str, 2))[2:].zfill(m // 4)
        
        output = {
            "status": "success",
            "requested_bits": m,
            "raw_bits_used": n,
            "hex": hex_val,
            "binary": bits_str
        }
        print(json.dumps(output))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
