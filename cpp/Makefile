# the compiler: gcc for C program, define as g++ for C++
CC = g++

# compiler flags:
#  -g     - this flag adds debugging information to the executable file
#  -Wall  - this flag is used to turn on most compiler warnings
CFLAGS  = -g -Wall -std=c++11

all: matmul mattrans fwalg competitor

matmul: matmul.cpp
	$(CC) $(CFLAGS) -o matmul matmul.cpp

mattrans: mattrans.cpp
	$(CC) $(CFLAGS) -o mattrans mattrans.cpp

fwalg: fwalg.cpp
	$(CC) $(CFLAGS) -o fwalg fwalg.cpp

competitor: competitor.cpp
	$(CC) $(CFLAGS) -o competitor competitor.cpp

clean:
	$(RM) matmul 
	$(RM) competitor