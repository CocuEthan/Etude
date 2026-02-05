/**
 * This program uses semaphores. Program 'example1' has A,B,C blocks and
 * 'example2' has D,E,F blocks. A runs before E and E runs before C.
 *
 *   example1  example2
 *
 *      A        D
 *       \---\
 *   V(S1)   |
 *           |  P(S1)
 *      B    \--> E
 *             V(S2)
 *           /---/ 
 *   P(S2)   |   
 *      C <--/    F
 *
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <errno.h>

#include "example.h"

int main() {
    int semid;
    struct sembuf op;

    // Get the semaphore set
    if((semid = semget(KEY, 0, 0)) == -1) {
        perror("Error getting semaphore set identifier");
        exit(EXIT_FAILURE);
    }

    printf("Block D\n");
    
    // P(S1)
    op.sem_num = S1;
    op.sem_op = -1;
    op.sem_flg = 0;
    if(semop(semid, &op, 1) == -1) {
        perror("Error on semaphore operation (1)");
        exit(EXIT_FAILURE);
    }

    printf("Block E\n");

    // V(S2)
    op.sem_num = S2;
    op.sem_op = 1;
    op.sem_flg = 0;
    if(semop(semid, &op, 1) == -1) {
        perror("Error on semaphore operation (2)");
        exit(EXIT_FAILURE);
    }

    printf("Block F\n");

    return EXIT_SUCCESS;
}