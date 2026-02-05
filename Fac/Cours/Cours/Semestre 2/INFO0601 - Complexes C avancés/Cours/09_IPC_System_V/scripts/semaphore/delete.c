/**
 * This program deletes a semaphore set; key is passed as argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/sem.h>

int main(int argc, char *argv[]) {
    int semid;
    key_t key;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "You must specify the key as parameter.\n");
        exit(EXIT_FAILURE);
    }
    key = (key_t)atoi(argv[1]);

    // Get the semaphore set
    if((semid = semget(key, 0, 0)) == -1) {
        perror("Error getting semaphore set identifier");
        exit(EXIT_FAILURE);
    }

    // Delete the semaphore set
    if(semctl(semid, IPC_RMID, 0) == -1) {
        perror("Error deleting semaphore set");
        exit(EXIT_FAILURE);
    }
    printf("Semaphore set deleted.\n");

    return EXIT_SUCCESS;
}