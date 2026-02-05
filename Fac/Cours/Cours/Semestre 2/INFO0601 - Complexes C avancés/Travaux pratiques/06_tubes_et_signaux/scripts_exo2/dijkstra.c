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

/**
 * Initialize a semaphore set.
 * @param pid the pid of the server
 * @return the semaphore set configuration
 */
sem_t sem_init(pid_t pid) {
    sem_t result;
    
    // Check if the server exists
    // #TODO#
    
    result.server_pid = pid;
    
    // Block SIGRTMIN
    // #TODO#
    
    return result;
}

/**
 * Clean the semaphore set.
 * @param sem the semaphore set
 */
void sem_clean(sem_t sem) {
    // Nothing to do
}

/**
 * P semaphore operation
 * @param sem the semaphore set configuration
 * @param num the semaphore number
 * @return 1 on success
 */
int sem_P(sem_t sem, int num) {    
    // Send signal to the server (SIGRTMIN+1) for P operation with value "num"
    // #TODO#
    
    // Wait for the server response (SIGRTMIN)
    // #TODO#
    
    return 0; // value sent by the server
}

/**
 * V semaphore operation
 * @param sem the semaphore set configuration
 * @param num the semaphore number
 * @return 1 on success 
 */
int sem_V(sem_t sem, int num) {
    // Send signal to the server (SIGRTMIN+2) for V operation with value "num"
    // #TODO#

    // Wait for the server response (SIGRTMIN)
    // #TODO#
    
    return 0; // value sent by the server
}