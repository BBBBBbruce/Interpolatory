# benches interpolators and saves to Interpolatory/Output

interpolators = ['Nearest', 'Oversample', 'Linear', 'SepConvL1-CUDA', 'SepConvLf-CUDA', 'RRIN-MidFrame-CUDA', 'RRIN-Linear-CUDA']

# run from Interpolatory/Simulator/python/ 
import os

for i in interpolators:
    print(f'===== {i} =====')
    os.system(f'mkdir -p ../../Output/Benchmark/{i}')
    os.system(f'python3 main.py -b {i} ../../Output/Benchmark/{i}')



