#!/bin/bash

mkdir -p logs_fw

for comp_size in 5 4 3 2 1 0
do

    for mthd in transposed recursive
    do

        for i in 0 1 2
        do
        
            echo $mthd $comp_size $i

            ./competitor $comp_size 23 &

            comp_pid=$!

            (/usr/bin/time -v ./fwalg $mthd) &> ./logs_fw/${mthd}_${comp_size}_${i} &

            wait -n

            pkill -15 competitor

            sleep 2

        done

    done

done
