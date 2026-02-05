#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "share.h"

/**
 * Get a shared array.
 * @param variable_name the name of the array
 * @return the shared array
 */
share_t share_init(char *variable_name) {
    share_t result;
    
    // Block SIGRTMIN+3 signal
    // #TODO#  
    
    // Check filename size
    if(strlen(variable_name) > MAX_LENGTH) {
        fprintf(stderr, "Length of array name is too long (max. %d)\n", MAX_LENGTH);
        exit(EXIT_FAILURE);
    }
    sprintf(result.filename, "/tmp/%s", variable_name);
    
    // Open fifo
    // #TODO# (fill result.fd)
    
    // Send request in the fifo for getting size of the array
    // #TODO#
    
    // Wait for response (SIGRTMIN+3): received value is the size of the array
    // #TODO# (fill result.size)
    
    return result;
}

/**
 * Clean a shared array.
 * @param array the shared array
 */
void share_clean(share_t array) {
    // Close fifo
    // #TODO#
}

/**
 * Get the size of the array.
 * @param array the shared array
 * @return the cell value
 */
int share_size(share_t array) {
    return array.size;
}

/**
 * Get a cell value.
 * @param array the shared array
 * @param cell the number of the cell
 * @return the cell value
 */
int share_get(share_t array, int cell) {
    int value = 0;
    //share_request_t request;
    
    if((cell < 0) || (cell >= array.size)) {
        fprintf(stderr, "Invalid cell number (max. %d)\n", array.size);
        exit(EXIT_FAILURE);
    }
    
    /*request.type = REQUEST_GET;
    request.pid = getpid();
    request.cell = cell;*/

    // Send request in the fifo 
    // #TODO#
    
    // Wait for response (SIGRTMIN+3)
    // #TODO# (fill value)
    
    return value;
}

/**
 * Get a cell value.
 * @param array the shared array
 * @param cell the number of the cell
 * @return the cell value
 */
void share_set(share_t array, int cell, int value) {
    //share_request_t request;
    
    if((cell < 0) || (cell >= array.size)) {
        fprintf(stderr, "Invalid cell number (max. %d)\n", array.size);
        exit(EXIT_FAILURE);
    }
    
    /*request.type = REQUEST_SET;
    request.pid = getpid();
    request.cell = cell;
    request.value = value;*/

    // Send request
    // #TODO#
    
    // Wait for response (SIGRTMIN+3): just an acknowledgment
    // #TODO#
}