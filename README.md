# Cache Simulator

## Installation

```bash
cd cs5234_cache  # or to whichever subfolder file is in
pip install -e .
```

## Python Example

```python
cs = Simulator(memory_size=65525, cache_size=64, block_size=4)

var_addr = cs.allocate()                          # allocate variable
array_addr = cs.allocate(10)                      # allocate 1d array
matrix_addr = cs.allocate(64, 64, default_val=0)  # allocate 2d array

cs.write(var_addr, value=10)                      # var = 10
cs.write(matrix_addr, 10, 10, value=50)           # matrix[10][10] = 50

cs.increment(var_addr, value=10)                  # var += 10

print(cs.read(matrix_addr, 10, 10))               # prints matrix[10][10]

print(cs.get_access_summary())                    # get hit/miss counts
```

## Running Matrix Multiplication

```bash
python matmul.py -N {matrix size} -B {block size} -M {cache size}
```

- Matrix size should be a power of 2.
- Block size is the size of each cache block (in number of integers)
- Cache size is the size of entire cache (in number of integers)

## Limitations

- Currently data type fixed to int (very easily changeable - change datatype of array in Block)
