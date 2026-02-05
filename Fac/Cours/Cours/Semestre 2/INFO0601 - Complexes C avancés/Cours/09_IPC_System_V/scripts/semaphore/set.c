/**
 * This program modifies the value of a semaphore of a set.
 * It takes as arguments the set key, the semaphore number and the new value.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/sem.h>

int main(int argc, char *argv[]) {
    key_t key;
    int num = -1, value, i, semid;
    unsigned short *values;
    struct semid_ds sem_buf;
    
    // Check arguments
    if((argc != 3) && (argc != 4)) {
        fprintf(stderr, "This programs modifies the value of one or all semaphores in a set.\n");
        fprintf(stderr, "Use: %s key [num] val\n", argv[0]);
        fprintf(stderr, "\tkey: the key of the semaphore set\n");
        fprintf(stderr, "\tnum: the semaphore number (if not specified, the value of all semaphore is modified)\n");
        fprintf(stderr, "\tval: the new value of the semaphore or all of semaphores\n");
        exit(EXIT_FAILURE);
    }
    
    // Get arguments values
    key = (key_t)atoi(argv[1]);
    if(argc == 4) {
        num = atoi(argv[2]);
        value = atoi(argv[3]);
    }
    else
        value = atoi(argv[2]);

    // Get the semaphore set identifier
    if((semid = semget(key, 0, 0)) == -1) {
        perror("Error getting semaphore set identifier");
        exit(EXIT_FAILURE);
    }

    if(num != -1) {
        // Changing the value of the specified semaphore
        if(semctl(semid, num, SETVAL, value) == -1) {
            perror("Error changing value of the semaphore");
            exit(EXIT_FAILURE);
        }
        printf("The semaphore value S%d is now %d\n", num, value);
    }
    else {
        // Get informations
        if(semctl(semid, 0, IPC_STAT, &sem_buf) == -1) {
            perror("Error getting informations on semaphore set");
            exit(EXIT_FAILURE);
        }

        // Create an array and initialize it
        if((values = malloc(sizeof(unsigned short) * sem_buf.sem_nsems)) == NULL) {
            perror("Error allocating array");
            exit(EXIT_FAILURE);
        }
        for(i = 0; i < sem_buf.sem_nsems; i++)
            values[i] = value;
                
        // Changing the value of the semaphores
        if(semctl(semid, 0, SETALL, values) == -1) {
            perror("Error changing value of the semaphores");
            exit(EXIT_FAILURE);
        }
        printf("The value of the semaphores is now %d\n", value);
        
        free(values);
    }

    return EXIT_SUCCESS;
}