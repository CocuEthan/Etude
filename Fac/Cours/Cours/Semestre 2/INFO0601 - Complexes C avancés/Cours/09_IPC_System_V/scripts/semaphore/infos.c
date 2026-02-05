/**
 * This program gets the informations of a semaphore set whose key is passed as
 * an argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/sem.h>

int main(int argc, char *argv[]) {
    int semid;
    key_t key;
    struct semid_ds sem_buf;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "You must specify the key as argument.\n");
        exit(EXIT_FAILURE);
    }
    key = (key_t)atoi(argv[1]);

    // Get the semaphore set identifier
    if((semid = semget(key, 0, 0)) == -1) {
        perror("Error getting semaphore set identifier");
        exit(EXIT_FAILURE);
    }

    // Get informations
    if(semctl(semid, 0, IPC_STAT, &sem_buf) == -1) {
        perror("Error getting informations on semaphore set");
        exit(EXIT_FAILURE);
    }

    // Display informations
    if(sem_buf.sem_otime == 0)
        printf("Last operation      : no operation yet\n");
    else
        printf("Last operation      : %s", ctime(&sem_buf.sem_otime));
    printf("Last modification   : %s", ctime(&sem_buf.sem_ctime));
    printf("Number of semaphores: %ld\n", sem_buf.sem_nsems);

    return EXIT_SUCCESS;
}