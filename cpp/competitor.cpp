#include <iostream>
#include <fstream>
#include <string.h>
#include <chrono>
#include <random>

int main(int argc, char **argv) {
    
    std::string arg = argv[1];
    std::size_t pos;
    int r = std::stoi(arg, &pos);
    int steps = 5;
    int time_per_step = 4;
    int m = 1 << (r + steps);

    auto A = new int[m >> steps];

    std::random_device rd;
    std::mt19937 rng(rd());
    std::uniform_int_distribution<int> uni(0, m);

    std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point mid = std::chrono::steady_clock::now();
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();

    int x, y, z, k, p;
    int i = steps;
    while (1) {
        end = std::chrono::steady_clock::now();
        x = uni(rng) >> i;
        y = uni(rng) >> i;
        z = uni(rng) >> i;
        A[x] = A[y] + A[z];
        p += 1;
        if ((end - begin < std::chrono::seconds(steps * time_per_step)) &&
            (end - mid > std::chrono::seconds(time_per_step))) {
            mid = std::chrono::steady_clock::now();
            // std::cout << p << std::endl;
            p = 0;
            i -= 1;
            delete [] A;
            k = m >> i;
            A = new int[k];
            // std::cout << k << std::endl;
            // for (auto j = 0; j < k; j++) A[j] = j;
        }
    }

    delete [] A;

    return 0;
}