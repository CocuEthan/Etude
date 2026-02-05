/**
 * This program deletes a segment whose key has passed as an argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/shm.h>

int main(int argc, char *argv[]) {
    int shmid;
    key_t key;

    // Check the arguments
    if(argc != 2) {
        fprintf(stderr, "You must specify the key of the segment as argument.\n");
        exit(EXIT_FAILURE);
    }
    key = (key_t)atoi(argv[1]);

    // Get the segment
    if((shmid = shmget(key, 0, 0)) == -1) {
        perror("Error getting the segment");
        exit(EXIT_FAILURE);
    }

    // Delete the segment
    if(shmctl(shmid, IPC_RMID, 0) == -1) {
        perror("Error deleting the segment");
        exit(EXIT_FAILURE);
    }
    printf("Shared memory segment deleted.\n");

    return EXIT_SUCCESS;
}