#include <iostream>
#include <fstream>
#include <string.h>

#define N 2048


void transposed_naive(int *A, int *B) {
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            B[j * N + i] = A[i * N + j];
        }
    }
}


void transposed_recursive(int *A, int *B, int sub_n,
                             int a_r, int a_c, int b_r, int b_c) {
    if (sub_n <= 2) {
        for (auto i = 0; i < sub_n; i++) {
            for (auto j = 0; j < sub_n; j++) {
                B[(b_r + i) * N + (b_c + j)] = A[(a_r + j) * N + (a_c + i)];
            }
        }
    }
    else {
        sub_n = sub_n / 2;
        transposed_recursive(A, B, sub_n, a_r, a_c, b_r, b_c);
        transposed_recursive(A, B, sub_n, a_r, a_c + sub_n, b_r + sub_n, b_c);
        transposed_recursive(A, B, sub_n, a_r + sub_n, a_c, b_r, b_c + sub_n);
        transposed_recursive(A, B, sub_n, a_r + sub_n, a_c + sub_n, b_r + sub_n, b_c + sub_n);
    }
}

void transposed_recursive(int *A, int *B){
    transposed_recursive(A, B, N, 0, 0, 0, 0);
}


int main(int argc, char **argv) {

    auto P = new int[N * N];
    auto P_T = new int[N * N];

    std::fstream P_data("P_data", std::ios_base::in);

    int p;
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            P_data >> p;
            P[i * N + j] = p;
        }
    }

    if(!strcmp(argv[1], "naive")) {
        transposed_naive(P, P_T);
    }
    else if(!strcmp(argv[1], "recursive")) {
        transposed_recursive(P, P_T);
    }

    std::fstream P_T_data("P_transposed", std::ios_base::out);
    for (auto i = 0; i < N; i++) {
        for (auto j = 0; j < N; j++) {
            P_T_data << P_T[i * N + j] << " ";
        }
    }

    delete [] P;
    delete [] P_T;

    return 0;
}