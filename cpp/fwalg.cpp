#include <iostream>
#include <fstream>
#include <string.h>
#include <algorithm>
#include <limits>

#define N 1024


void fw_naive(int *W) {
    for (auto k = 0; k < N; k++) {
        for (auto i = 0; i < N; i++) {
            for (auto j = 0; j < N; j++) {
                W[i * N + j] = std::min(W[i * N + j], W[i * N + k] + W[k * N + j]);
            }
        }
    }
}


void fw_transposed(int *W) {
    for (auto i = 0; i < N; i++) {
        for (auto k = 0; k < N; k++) {
            for (auto j = 0; j < N; j++) {
                W[i * N + j] = std::min(W[i * N + j], W[i * N + k] + W[k * N + j]);
            }
        }
    }
}


void fw_recursive_helper(int *W, int sub_n,
                             int a_r, int a_c, int b_r, int b_c, int c_r, int c_c) {
    if (sub_n <= 2) {
        for (auto k = 0; k < sub_n; k++) {
            for (auto i = 0; i < sub_n; i++) {
                for (auto j = 0; j < sub_n; j++) {
                    W[(i + c_r) * N + (j + c_c)] = std::min(
                        W[(i + c_r) * N + (j + c_c)], 
                        W[(a_r + i) * N + (a_c + k)] + W[(b_r + k) * N + (b_c + j)]);
                }
            }
        }
    }
    else {
        sub_n = sub_n / 2;
        for (int k = 0; k < 2; k++) {
            for (int i = 0; i < 2; i++) {
                for (int j = 0; j < 2; j++) {
                    int blk_r = i * sub_n;
                    int blk_c = j * sub_n;

                    int c_quad_r = c_r + blk_r;
                    int c_quad_c = c_c + blk_c;
                    int a_quad_r = a_r + blk_r;
                    int b_quad_c = b_c + blk_c;

                    int blk = k * sub_n;
                    int a_quad_c = a_c + blk;
                    int b_quad_r = b_r + blk;
                    fw_recursive_helper(W, sub_n, 
                        a_quad_r, a_quad_c, b_quad_r, b_quad_c, c_quad_r, c_quad_c);
                }
            }
        }
    }
}

void fw_recursive(int *W){
    fw_recursive_helper(W, N, 0, 0, 0, 0, 0, 0);
}


int main(int argc, char **argv) {

    auto W = new int[N * N];

    std::fstream W_data("W_data", std::ios_base::in);

    int w;
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            W_data >> w;
            W[i * N + j] = w;
        }
    }

    if(!strcmp(argv[1], "naive")) {
        fw_naive(W);
    }
    else if(!strcmp(argv[1], "transposed")) {
        fw_transposed(W);
    }
    else if(!strcmp(argv[1], "recursive")) {
        fw_recursive(W);
    }

    std::fstream SP_data("SP_data", std::ios_base::out);
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            SP_data << W[i * N + j] << " ";
        }
    }

    delete [] W;

    return 0;
}