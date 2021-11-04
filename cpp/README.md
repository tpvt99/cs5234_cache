# Cache Adaptivity On CPP

## Information

We test different matrix multiplication algorithm against changing cache by running another program simulataneously which uses a changing amount of memory. We then track the amount of page faults from the algorithm.

## Instruction

Building Docker and running

```bash
docker build -t simple_linux .

./docker_script.sh
```

Inside the VM

```bash
cd proj

make

./run_with_comp.sh
```
