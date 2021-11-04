#!/bin/bash

mkdir -p logs

for comp_size in 12 14 16 18 20 22
do
	
    for mthd in recursive naive transposed
    do
        
        for i in 0 1 2 3 4
        do
            echo $mthd $comp_size $i

            ./competitor $comp_size &

            comp_pid=$!

            # echo $comp_pid

            (/usr/bin/time -v ./matmul $mthd) &> ./logs/${mthd}_${comp_size}_${i} &

            wait -n

            pkill -15 competitor

            # ./competitor $comp_size &

            # (/usr/bin/time -v ./matmul $mthd) &> ./logs/${mthd}_${comp_size}_${i}

            sleep 2

        done

    done

done
