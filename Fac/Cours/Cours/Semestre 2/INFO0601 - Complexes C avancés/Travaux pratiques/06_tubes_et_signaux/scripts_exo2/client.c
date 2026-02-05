#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "dijkstra.h"

int main(int argc, char *argv[]) {
    sem_t sem;
    pid_t pid;
    
    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s PID where PID is the server PID\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    pid = atoi(argv[1]);
    
    // Main loop
    sem = sem_init(pid);    
    while(1) {
        sem_P(sem, 0);
        printf("Client enters critical section\n");
        sleep(5);
        printf("Client comes out critical section\n");        
        sem_V(sem, 0);
    }
    sem_clean(sem);
    
    return EXIT_SUCCESS;
}