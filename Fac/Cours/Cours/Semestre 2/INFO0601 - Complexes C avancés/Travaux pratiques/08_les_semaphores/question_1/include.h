#ifndef _INCLUDE
#define _INCLUDE

// Constants for sleep
#define MIN        100
#define MAX        1000

// Constants for pipes
#define READ       0
#define WRITE      1

// Block state
#define UNDEF     -1
#define START      0
#define END        1

// Blocks
#define A1         0
#define B1         1
#define C1         2
#define A2         3
#define B2         4
#define C2         5
#define A3         6
#define B3         7
#define C3         8

// Messages structure
typedef struct {
    int number;
    int action;
} message_t;

#endif