#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/wait.h>
#include <sys/types.h>

#include "include.h"

/**
 * Returns a random integer in intervalle [a, b].
 * YOU DON'T HAVE TO MODIFY IT
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Simulation of a code block of a child.
 * YOU DON'T HAVE TO MODIFY IT
 * @param fd the descriptor file of the pipe
 * @param number the block number
 */
void block(int fd, int number) {
    message_t msg;

    // Message to notify of start
    msg.number = number;
    msg.action = START;
    if(write(fd, &msg, sizeof(msg)) == -1) {
        perror("Error writing to parent (1)");
        exit(EXIT_FAILURE);
    }

    // Pause to simulate block execution
    usleep(random_integer(MIN, MAX));

    // Message to notify of end
    msg.action = END;
    if(write(fd, &msg, sizeof(msg)) == -1) {
        perror("Error writing to parent (1)");
        exit(EXIT_FAILURE);
    }
}

/**
 * Child #1 routine.
 * #TODO# Add semaphore operations before or after blocks
 * @param fd the descriptor file of the pipe
 */
void child1(int fd) {
    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?

    // Start block A1
    block(fd, A1);
    // End block A1

    // #TODO# Add a semaphore operation ?

    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?

    // Start block B1
    block(fd, B1);
    // End block B1

    // #TODO# Add a semaphore operation ?

    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?

    // Start block C1
    block(fd, C1);
    // End block C1

    // #TODO# Add a semaphore operation ?

    // Close pipe
    if(close(fd) == -1) {
        perror("Error closing pipe (child #1)");
        exit(EXIT_FAILURE);
    }

    exit(EXIT_SUCCESS);
}

/**
 * Child #2 routine.
 * #TODO# Add semaphore operations before or after blocks
 * @param fd the descriptor file of the pipe
 */
void child2(int fd) {
    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?

    // Start block A2
    block(fd, A2);
    // End block A2

    // #TODO# Add a semaphore operation ?

    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?
    
    // Start block B2
    block(fd, B2);
    // End block B2

    // #TODO# Add a semaphore operation ?
    
    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?
    
    // Start block C2
    block(fd, C2);
    // End block C2

    // #TODO# Add a semaphore operation ?
    
    // Close pipe
    if(close(fd) == -1) {
        perror("Error closing pipe (child #2)");
        exit(EXIT_FAILURE);
    }

    exit(EXIT_SUCCESS);
}

/**
 * Child #3 routine.
 * #TODO# Add semaphore operations before or after blocks
 * @param fd the descriptor file of the pipe
 */
void child3(int fd) {
    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?

    // Start block A3
    block(fd, A3);
    // End block A3

    // #TODO# Add a semaphore operation ?

    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?
    
    // Start block B3
    block(fd, B3);
    // End block B3

    // #TODO# Add a semaphore operation ?
    
    usleep(random_integer(MIN, MAX));

    // #TODO# Add a semaphore operation ?
    
    // Start block C3
    block(fd, C3);
    // End block C3
    
    // #TODO# Add a semaphore operation ?
    
    // Close pipe
    if(close(fd) == -1) {
        perror("Error closing pipe (child #3)");
        exit(EXIT_FAILURE);
    }

    exit(EXIT_SUCCESS);
}

/**
 * Main function.
 * @param argc the number of arguments
 * @param argv arguments
 * @return the return code
 */
int main(int argc, char *argv[]) {
    int i, n, error, errors = 0;
    pid_t _pipe[2];
    char *blocks[9] = { "A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3" };
    int states[9];
    message_t msg;

    // Initialization of block states
    for(i = 0; i < 9; i++)
        states[i] = UNDEF;

    // Create pipe to send messages from children to parent
    if(pipe(_pipe) == -1) {
        perror("Error creating pipe");
        exit(EXIT_FAILURE);
    }

    // Create children
    for(i = 1; i <= 3; i++) {
        if((n = fork()) == -1) {
            fprintf(stderr, "Error creating child #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        else if(n == 0) {
            // Close the pipe in reading for the child
            if(close(_pipe[READ]) == -1) {
                fprintf(stderr, "Error closing pipe in reading for child #%d\n", i);
                exit(EXIT_FAILURE);
            }

            // Initialization of the random number generator
            srand(time(NULL) + getpid());

            // Launch routines
            switch(i) {
                case 1: child1(_pipe[WRITE]); break;
                case 2: child2(_pipe[WRITE]); break;
                case 3: child3(_pipe[WRITE]); break;
            }
        }
    }

    // Close the pipe in writing for the parent
    if(close(_pipe[WRITE]) == -1) {
        fprintf(stderr, "Error closing pipe in writing for the parent\n");
        exit(EXIT_FAILURE);
    }

    // Reading actions: number of blocks x 2
    for(i = 0; i < 18; i++) {
        // Wait for message
        if(read(_pipe[READ], &msg, sizeof(msg)) == -1) {
            perror("Error reading message in parent");
            exit(EXIT_FAILURE);
        }

        // Display message
        if(msg.action == START) {
            // Check message
            error = 0;
            switch(msg.number) {
                case A1:
                    error = (states[B2] == START) || (states[A3] == START);
                    break;
                case A3:
                    error = (states[A1] == START) || (states[B2] == START);
                    break;
                case B2:
                    error = (states[A1] == START) || (states[A3] == START);
                    break;
                case C1:
                    error = (states[B2] != END) || (states[C3] != END);
                    break;
                case C3:
                    error = (states[B2] != END);
                    break;
            }

            // Display state
            printf("Start block #%s ", blocks[msg.number]);
            if(error) {
                errors++;
                printf("\033[0;31m[ERROR]\033[0m\n");
            }
            else
                printf("\033[0;32m[OK]\033[0m\n");
        }
        else
            printf("End block #%s\n", blocks[msg.number]);
        states[msg.number] = msg.action;
    }

    // Wait for children end
    for(i = 0; i < 3; i++) {
        if(wait(NULL) == -1) {
            perror("Error waiting child");
            exit(EXIT_FAILURE);
        }
    }

    // End message
    if(errors != 0)
        printf("Execution failed (it sucks!).\n");
    else
        printf("Execution was successful (this time).\n");

    return EXIT_SUCCESS;
}