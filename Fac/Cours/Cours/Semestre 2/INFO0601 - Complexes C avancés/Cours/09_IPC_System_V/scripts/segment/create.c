/**
 * Program illustrating how shmget works to create a shared memory segment. It
 * creates a 1000 octets segment (size must be changed according to the usage).
 * @author Cyril Rabat
 */
#define KEY 2022 // Key for segment
#define SIZE 1000 // Size of the segment

#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <errno.h>

int main() {
    int shmid;

    // Create the segment
    if((shmid = shmget(KEY, SIZE, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        if(errno == EEXIST)
            fprintf(stderr, "Segment (key=%d) already exists\n", KEY);
        else
            perror("Error creating segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment (key=%d, id=%d) created successfully...\n", KEY, shmid);

    return EXIT_SUCCESS;
}
