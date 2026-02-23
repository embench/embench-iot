#include "support.h"
#include "sudoku_search.h"

int8_t board[BOARD_SIZE][BOARD_SIZE];

const int8_t hardcoded_board[BOARD_SIZE][BOARD_SIZE] = {
    { 1,  0,  4,  0, 25, 19,  0,  0, 10, 21,  8,  0, 14,  0,  6, 12,  9,  0,  0,  0,  0,  0,  0,  0,  5},
    { 5,  0, 19, 23, 24,  0, 22, 12,  0, 16,  6,  0, 20,  0, 18,  0, 25, 14, 13, 10, 11,  0,  0,  1, 15},
    { 0,  0,  0,  0,  0,  0, 21,  5,  0, 20, 11, 10,  0,  1,  0,  4,  8, 24, 23, 15, 18,  0, 16, 22, 19},
    { 0,  7, 21,  8, 18,  0,  0, 11,  0,  5,  0, 24,  0,  0,  0, 17, 22,  1,  9,  6, 25,  0,  0,  0,  0},
    { 0, 13, 15,  0, 22, 14,  0, 18,  0, 16,  0,  0,  0,  4,  0,  0,  0, 19,  0,  0,  0, 24, 20, 21, 17},
    {12,  0, 11,  0,  6,  0,  0,  0, 15,  0,  0,  0,  0, 21, 25, 19,  0,  4,  0, 22, 14,  0,  0, 20,  0},
    { 8,  0,  0, 21,  0, 16,  0,  0,  2,  0,  3,  0,  0,  0,  0, 17, 23, 18, 22,  0,  0,  0, 24,  6,  0},
    { 4,  0, 14, 18,  7,  9,  0, 22, 21, 19,  0,  0,  2,  0,  5,  0,  0,  6, 16, 15,  0,  0,  0, 11, 12},
    {22,  0, 24,  0, 23,  0, 11,  0,  7,  0,  4,  0, 14,  0,  2, 12,  0,  8,  5, 19,  0, 25,  9,  0,  0},
    {20,  0,  0,  0,  5,  0,  0,  0, 17,  9, 12, 18,  0,  1,  0,  7, 24,  0,  0,  0,  0,  0,  0, 13,  4},
    {13,  0,  0,  5,  0,  2, 23, 14,  4, 18, 22,  0, 17,  0, 20,  0,  1,  9, 21, 12,  0,  0,  8, 11,  0},
    {14, 23,  0, 24,  0,  0,  0,  0,  0,  0, 20, 25,  0,  3,  4, 13,  0, 11, 21,  9,  5, 18, 22,  0,  0},
    { 7,  0,  0, 11, 17, 20, 24,  0,  0,  3,  4,  1, 12,  0,  0,  0,  6, 14,  0,  0,  5, 25, 13,  0,  0},
    { 0,  0, 16,  9,  0, 17, 11,  7, 10, 25,  0, 13,  6,  0, 18,  0,  0, 19,  4,  0,  0,  0,  0,  0, 20},
    { 6, 15,  0, 19,  4, 13,  0,  0,  5,  0, 18, 11,  0,  0,  9,  8, 22, 16, 25, 10,  7,  0,  0,  0,  0},
    { 0,  0,  0,  2,  0, 10, 19,  3,  0,  1,  0, 22,  9,  4, 11, 15,  0, 20,  0,  8,  0, 23,  0,  0, 25},
    { 0, 24,  8, 13,  1,  0,  4, 20,  0, 17, 14,  0,  0, 18,  0,  0, 16, 22,  5,  0,  0, 11,  0, 10,  0},
    {23, 10,  0,  0,  0,  0,  0, 18,  0,  6,  0, 16,  0,  0, 17,  1,  0, 13,  0,  3,  0, 19, 12,  0,  0},
    {25,  5,  0, 14, 11,  0, 17,  0,  8, 24, 13,  0, 19, 23, 15,  9,  0, 12,  0, 20,  0, 22,  0,  7,  0},
    { 0,  0, 17,  4,  0, 22, 15,  0, 23, 11, 12, 25,  0,  0,  0, 18,  8,  0,  7,  0, 14,  0,  0, 13,  0},
    {19,  6, 23, 22,  8,  0,  0,  1, 25,  4, 14,  2,  0,  3,  7, 13, 10, 11, 16,  0,  0,  0,  0,  0,  0},
    { 0,  4,  0, 17,  0,  3,  0, 24,  0,  8, 20, 23, 11, 10, 25, 22,  0,  0, 12, 13,  2, 18,  6,  0,  0},
    { 0,  0,  7, 16,  0,  0,  6, 17,  2, 21,  0, 18,  0,  0,  0, 19,  0,  0,  8,  0,  0,  0,  0,  4,  0},
    {18,  9, 25,  1,  2, 11,  0,  0, 13, 22,  4,  0, 21,  0,  5,  0, 23,  7,  0,  0, 15,  0,  3,  0,  8},
    { 0, 21, 10,  0,  0, 12,  0, 20, 16,  0, 19,  0,  0,  0,  0, 15, 14,  4,  2, 18, 23, 25, 11,  7,  0}
};

static int is_safe(int row, int col, int8_t num) {
    for (int x = 0; x < BOARD_SIZE; x++) {
        if (board[row][x] == num) return 0;
        if (board[x][col] == num) return 0;
    }

    int startRow = row - (row % SUBGRID_SIZE);
    int startCol = col - (col % SUBGRID_SIZE);
    for (int i = 0; i < SUBGRID_SIZE; i++) {
        for (int j = 0; j < SUBGRID_SIZE; j++) {
            if (board[i + startRow][j + startCol] == num) return 0;
        }
    }
    return 1;
}

static int solve() {
    int row = -1, col = -1;
    int empty = 0;

    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == 0) {
                row = i; col = j; empty = 1; break;
            }
        }
        if (empty) break;
    }

    if (!empty) return 1;

    for (int8_t num = 1; num <= BOARD_SIZE; num++) {
        if (is_safe(row, col, num)) {
            board[row][col] = num;
            if (solve()) return 1;
            board[row][col] = 0;
        }
    }
    return 0;
}

/* Embench API Functions */

void initialise_benchmark() {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            board[i][j] = hardcoded_board[i][j];
        }
    }
}

void warm_caches(int heat) {
    initialise_benchmark();
    benchmark();
}

int __attribute__ ((noinline)) benchmark(void) {
    return solve();
}

int verify_benchmark(int res) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        for (int j = 0; j < BOARD_SIZE; j++) {
            if (board[i][j] == 0) return 0; // Test Failed

            int8_t temp = board[i][j];
            board[i][j] = 0;
            if (!is_safe(i, j, temp)) return 0; // Test Failed
            board[i][j] = temp;
        }
    }
    return 1; // Test Passed
}