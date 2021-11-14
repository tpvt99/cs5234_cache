# #!/bin/bash

# mkdir -p logs_trans

# for comp_size in 16 20 24 28 32
# do
	
#     for mthd in recursive naive
#     do
        
#         for i in 0 1 2 3 4
#         do
#             echo $mthd $comp_size $i

#             ./competitor $comp_size &

#             comp_pid=$!

#             (/usr/bin/time -v ./mattrans $mthd) &> ./logs_trans/${mthd}_${comp_size}_${i} &

#             wait -n

#             pkill -15 competitor

#             sleep 2

#         done

#     done

# done
