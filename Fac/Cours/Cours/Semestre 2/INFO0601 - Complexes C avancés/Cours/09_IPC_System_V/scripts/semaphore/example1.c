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
    unsigned short val[2] = { 0, 0 };
    struct sembuf op;

    // Create the semaphore set
    if((semid = semget(KEY, NUMBER, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        if(errno == EEXIST)
            fprintf(stderr, "Set (key=%d) already exists\n", KEY);
        else
            perror("Error creating set");
        exit(EXIT_FAILURE);
    }
    
    // Initialize the set
    if(semctl(semid, 0, SETALL, val) == -1) {
        perror("Error initializing");
        exit(EXIT_FAILURE);
    }
    
    printf("Block A\n");
    
    // V(S1)
    op.sem_num = S1;
    op.sem_op = 1;
    op.sem_flg = 0;
    if(semop(semid, &op, 1) == -1) {
        perror("Error on semaphore operation (1)");
        exit(EXIT_FAILURE);
    }

    printf("Block B\n");

    // P(S2)
    op.sem_num = S2;
    op.sem_op = -1;
    op.sem_flg = 0;
    if(semop(semid, &op, 1) == -1) {
        perror("Error on semaphore operation (2)");
        exit(EXIT_FAILURE);
    }

    printf("Block C\n");

    return EXIT_SUCCESS;
}