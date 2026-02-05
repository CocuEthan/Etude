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

int main() {
    int shmid, i;
    int *address;

    // Get the segment identifier
    if((shmid = shmget(KEY, 0, 0)) == -1) {
        perror("Error getting the segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment identifier obtained\n");
    
    // Attach the segment
    if((address = shmat(shmid, NULL, 0)) == (void*)-1) {
        perror("Error attaching the segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment attached\n");

    // Display content
    printf("Segment content: [");
    for(i = 1; i <= address[0]; i++) {
        printf("%d", address[i]);
        if(i < address[0]) printf(", ");
    }
    printf("]\n");
    
    // Detach segment
    if(shmdt(address) == -1) {
        perror("Error detaching segment");
        exit(EXIT_FAILURE);
    }
    printf("Segment detached\n");

    return EXIT_SUCCESS;
}