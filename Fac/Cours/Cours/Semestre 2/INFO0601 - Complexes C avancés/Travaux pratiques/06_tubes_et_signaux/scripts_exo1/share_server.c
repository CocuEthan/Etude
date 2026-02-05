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

// Name of the fifo
char filename[256];

// Stop variable for the main loop
int stop = 0;

/**
 * Clean procedure.
 */
void end() {
    // Delete fifo
    // #TODO#
}

/**
 * Handler for SIGINT signal.
 * @param signum the received signal number
 */
void handler(int signum) {
    stop = 1;
}

int main(int argc, char *argv[]) {
    int *var;
    int size, i;
    //int value;
    share_request_t request;
    size_t n = 0;
    
    // Check arguments
    if(argc < 3) {
        fprintf(stderr, "Use: %s name value1 ... valueX\n", argv[0]);
        fprintf(stderr, "Create a shared array with X cells\n");
        fprintf(stderr, "  where:\n");
        fprintf(stderr, "    name: the name of the shared array (max. %d characters)\n", MAX_LENGTH);
        fprintf(stderr, "    valueX: the value of the cell X (max. %d values)\n", MAX_SIZE);
        exit(EXIT_FAILURE);
    }
    if(strlen(argv[1]) > MAX_LENGTH) {
        fprintf(stderr, "The name must have less than %d characters.\n", MAX_LENGTH);
        exit(EXIT_FAILURE);
    }
    if(argc > MAX_SIZE + 2) {
        fprintf(stderr, "The number of cells must be less than %d.\n", MAX_SIZE);
        exit(EXIT_FAILURE);
    }
    size = argc - 2;
    
    // Specify the SIGINT handler
    // #TODO#
    
    sprintf(filename, "/tmp/%s", argv[1]);
    // Create the fifo
    // #TODO#
    
    // Register cleaning procedure
    // #TODO#
    
    // Allocating array
    if((var = malloc(size * sizeof(int))) == NULL) {
        perror("Error allocating array");
        exit(EXIT_FAILURE);
    }
    
    // Initializing array
    for(i = 0; i < size; i++) {
        var[i] = atoi(argv[i + 2]);
    }
    
    // Open fifo
    // #TODO#
    
    while(stop == 0) {
        // Read next request
        // #TODO# (fill n - the number of read octets - and request)
        
        if(n == 0) {
            printf("No more client...\n");
            stop = 1;
        }
        else {
            if((request.cell >= 0) && (request.cell < size)) {
                //value = -1;
                switch(request.type) {
                    case REQUEST_GET:
                        //value = var[request.cell];
                        break;
                    case REQUEST_SET:
                        var[request.cell] = request.value;
                        //value = var[request.cell];
                        break;
                    case REQUEST_SIZE:
                        //value = size;
                        break;
                }
                
                // Send response (SIGRTMIN+3) with the value
                // #TODO#
            }
        }
    }
    
    // Close fifo
    // #TODO#
    
    return EXIT_SUCCESS;
}