#include <iostream>
#include <fstream>
#include <string.h>

#define N 1024


void matmul_naive(int *A, int *B, int *C) {
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            for (auto k = 0; k < N; k++) {
                C[i * N + j] += A[i * N + k] * B[k * N + j];
            }
        }
    }
}


void matmul_transposed(int *A, int *B, int *C) {
    for (auto i = 0; i < N; i++) {
        for (auto k = 0; k < N; k++) {
            for (auto j = 0; j< N; j++) {
                C[i * N + j] += A[i * N + k] * B[k * N + j];
            }
        }
    }
}


void matmul_recursive_helper(int *A, int *B, int *C, int sub_n,
                             int a_r, int a_c, int b_r, int b_c, int c_r, int c_c) {
    if (sub_n <= 2) {
        for (auto i = 0; i < sub_n; i++) {
            for (auto k = 0; k < sub_n; k++) {
                for (auto j = 0; j < sub_n; j++) {
                    C[(i + c_r) * N + (j + c_c)] += A[(a_r + i) * N + (a_c + k)] * B[(b_r + k) * N + (b_c + j)];
                }
            }
        }
    }
    else {
        sub_n = sub_n / 2;
        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                int blk_r = i * sub_n;
                int blk_c = j * sub_n;

                int c_quad_r = c_r + blk_r;
                int c_quad_c = c_c + blk_c;
                int a_quad_r = a_r + blk_r;
                int b_quad_c = b_c + blk_c;

                for (int k = 0; k < 2; k++) {
                    int blk = k * sub_n;
                    int a_quad_c = a_c + blk;
                    int b_quad_r = b_r + blk;
                    matmul_recursive_helper(A, B, C, sub_n, 
                        a_quad_r, a_quad_c, b_quad_r, b_quad_c, c_quad_r, c_quad_c);
                }
            }
        }
    }
}

void matmul_recursive(int *A, int *B, int *C){
    matmul_recursive_helper(A, B, C, N, 0, 0, 0, 0, 0, 0);
}


int main(int argc, char **argv) {

    auto A = new int[N * N];
    auto B = new int[N * N];
    auto C = new int[N * N];

    std::fstream A_data("A_data", std::ios_base::in);
    std::fstream B_data("B_data", std::ios_base::in);

    int a, b;
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            A_data >> a;
            B_data >> b;
            A[i * N + j] = a;
            B[i * N + j] = b;
            C[i * N + j] = 0;
        }
    }

    if(!strcmp(argv[1], "naive")) {
        matmul_naive(A, B, C);
    }
    else if(!strcmp(argv[1], "transposed")) {
        matmul_transposed(A, B, C);
    }
    else if(!strcmp(argv[1], "recursive")) {
        matmul_recursive(A, B, C);
    }

    std::fstream C_data("C_data", std::ios_base::out);
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            C_data << C[i * N + j] << " ";
        }
    }

    delete [] A;
    delete [] B;
    delete [] C;

    return 0;
}