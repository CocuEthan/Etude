/**
 * This program uses semget to create a semaphore set.
 * @author Cyril Rabat
 */
#define KEY 1940 // Key for the set (Chuck Norris birthdate)
#define NUMBER 5 // Number of semaphores in the set

#include <stdio.h>
#include <stdlib.h>
#include <sys/sem.h>
#include <sys/stat.h>
#include <errno.h>

int main() {
    int semid;

    // Create the semaphore set
    if((semid = semget(KEY, NUMBER, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        if(errno == EEXIST)
            fprintf(stderr, "Set (key=%d) already exists\n", KEY);
        else
            perror("Error creating the semaphore set");
        exit(EXIT_FAILURE);
    }
    printf("Set (key=%d, id=%d) created successfully...\n", KEY, semid);

    return EXIT_SUCCESS;
}