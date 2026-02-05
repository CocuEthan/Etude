/**
 * This program displays the value of one or all of the semaphores in a set.
 * The key is passed as argument.
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
    
    // Display help
    if((argc != 2) && (argc != 3)) {
        fprintf(stderr, "This program displays the value of one or all of the semaphores in a set.\n");
        fprintf(stderr, "Use: %s key [num]\n", argv[0]);
        fprintf(stderr, "\tkey: the key of the semaphore set\n");
        fprintf(stderr, "\tnum: the number of the semaphore (if not specified, the values of all semaphores are displayed)\n");
        exit(EXIT_FAILURE);
    }
    key = (key_t)atoi(argv[1]);
    if(argc == 3)
        num = atoi(argv[2]);

    // Get the semaphore set
    if((semid = semget(key, 0, 0)) == -1) {
        perror("Error getting semaphore set identifier");
        exit(EXIT_FAILURE);
    }

    if(num != -1) {
        // Get the value of the semaphore specified
        if((value = semctl(semid, num, GETVAL)) == -1) {
            perror("Error getting the semaphore value");
            exit(EXIT_FAILURE);
        }
        printf("The value of the semaphore S%d is %d\n", num, value);
    }
    else {
        // Get informations on the semaphore set
        if(semctl(semid, 0, IPC_STAT, &sem_buf) == -1) {
            perror("Error getting informations on the semaphore set");
            exit(EXIT_FAILURE);
        }
        
        if((values = malloc(sizeof(unsigned short) * sem_buf.sem_nsems)) == NULL) {
            perror("Error allocating buffer");
            exit(EXIT_FAILURE);
        }
        
        // Get the values of all semaphores
        if(semctl(semid, 0, GETALL, values) == -1) {
            perror("Error getting values");
            exit(EXIT_FAILURE);
        }
        
        printf("Values:\n");
        for(i = 0; i < sem_buf.sem_nsems; i++) {
            printf("\tS%d = %d\n", i, values[i]);
        }
        
        free(values);
    }

    return EXIT_SUCCESS;
}