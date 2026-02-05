/**
 * This program uses a segment to share an array of integers.
 * memory1: crée et initialise le segment de mémoire partagée
 * memory2: get and display the segment content
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <errno.h>

#include "memory.h"

#define SIZE 15

int main() {
    int shmid, i;
    int *address;

    // Create and get the segment identifier
    if((shmid = shmget(KEY, sizeof(int) * (SIZE + 1), S_IRUSR | S_IWUSR | IPC_CREAT)) == -1) {
        perror("Error creating the segment or getting the segment identifier");
        exit(EXIT_FAILURE);
    }
    printf("Segment created and identifier obtained\n");
    
    // Attach the segment
    if((address = shmat(shmid, NULL, 0)) == (void*)-1) {
        perror("Error attaching segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment attached\n");

    // Initialization
    address[0] = SIZE;
    for(i = 1; i <= SIZE; i++)
        address[i] = i * 2;
    printf("Segment initialized\n");
    
    // Detach the segment
    if(shmdt(address) == -1) {
        perror("Error detaching the segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment detached\n");

    return EXIT_SUCCESS;
}
