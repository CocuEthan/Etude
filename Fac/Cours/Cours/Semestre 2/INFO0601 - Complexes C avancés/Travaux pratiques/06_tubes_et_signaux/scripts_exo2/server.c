#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "dijkstra.h"
#include "queue.h"

int main(int argc, char *argv[]) {
    int *sems;
    queue_t *waiting_queue;
    
    int signal = 0, size, i, value;
    pid_t pid;

    // Check arguments
    if(argc < 2) {
        fprintf(stderr, "Use: %s value1 ... valueX\n", argv[0]);
        fprintf(stderr, "Create a semaphore set with n semaphores\n");
        fprintf(stderr, "  where:\n");
        fprintf(stderr, "    valueX: the initial value of the semaphore X (max. %d values)\n", MAX_SEMS);
        exit(EXIT_FAILURE);
    }
    if(argc > MAX_SEMS + 1) {
        fprintf(stderr, "The number of semaphores must be less than %d.\n", MAX_SEMS);
        exit(EXIT_FAILURE);
    }
    size = argc - 1;
        
    // Allocating set
    if((sems = malloc(size * sizeof(int))) == NULL) {
        perror("Error allocating set");
        exit(EXIT_FAILURE);
    }
    
    // Initializing array
    for(i = 0; i < size; i++) {
        sems[i] = atoi(argv[i + 1]);
    }
    
    // Allocating waiting queues
    if((waiting_queue = malloc(size * sizeof(queue_t))) == NULL) {
        perror("Error allocating queues");
        exit(EXIT_FAILURE);
    }
    
    // Initializing array
    for(i = 0; i < size; i++) {
        waiting_queue[i] = queue_init();
    }
    
    // Block SIGRTMIN+1 and SIGRTMIN+2
    // #TODO#
    
    printf("My PID: %d\n", getpid());
    
    while(1) {
        // Wait for an operation (SIGRTMIN+1 or SIGRTMIN+2) with sigwaitinfo
        // signal variable is the received signal number
        // #TODO#
        
        // Get the value sent by signal
        value = 0; // #TODO#
        
        // Get the PID of the transmitter
        pid = 0; // #TODO#
    
        if((value >= 0) && (value < size)) {
            // Semaphore number is valid
            
            if(signal == SIGRTMIN+1) {
                // P operation
                if(sems[value] > 0) {
                    // Decrement semaphore
                    printf("%d: P(S%d) authorized\n", pid, value);
                    sems[value]--;
                    
                    // Send SIGRTMIN with value 1 to the transmitter
                    // #TODO#
                }
                else {
                    // Queuing PID of the signal transmitter if queue isn't full
                    if(queue_isfull(&waiting_queue[value])) {
                        // Queue is full
                        printf("S%d queue is full!\n", value);
                        
                        // Send SIGRTMIN with value 0 to the transmitter
                        // #TODO#
                    }
                    else {
                        // Queue is'nt full: queuing pid
                        printf("%d: blocked on P(S%d)\n", pid, value);
                        queue_add(&waiting_queue[value], pid);
                    }
                }
            }
            else {
                // V operation
                
                // Increment semaphore
                sems[value]++;
                printf("%d: V(S%d)\n", pid, value);
                
                // Send SIGRTMIN with value 1 to the transmitter
                // #TODO#
                
                // If queue isn't empty, deblock the next process
                if(!queue_isempty(&waiting_queue[value])) {
                    // Decrement semaphore
                    sems[value]--;
                    
                    // Get PID of the next process
                    pid = queue_get(&waiting_queue[value]);
                    printf("%d: deblocked on P(S%d)\n", pid, value);
                    
                    // Send SIGRTMIN with value 1 to pid
                    // #TODO#
                }
            }
        }
        else {
            // Semaphore number is invalid
            printf("%d: bad semaphore (%d)\n", pid, value);
            
            // Send error to the transmitter (signal SIGRTMIN with value 0)
            // #TODO#
        }
    }
    
    return EXIT_SUCCESS;
}