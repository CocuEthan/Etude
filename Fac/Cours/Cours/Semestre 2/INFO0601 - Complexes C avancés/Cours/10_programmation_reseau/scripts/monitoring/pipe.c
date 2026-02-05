/**
 * This program illustrates the file descriptor monitoring with pselect.
 * It creates X children that send data through pipes. The father waits for
 * data received in the tubes.
 */
#include <time.h>
#include <sys/select.h>
#include <sys/types.h>
#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

int stop = 0;

/**
 * Return a random integer in the interval [a,b].
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Function of each child.
 * @param num the number of the child
 * @param out the file descriptor of the pipe
 */
void child(int num, int out) {
    srand(time(NULL) + num);

    while(1) {
        sleep(random_integer(1, 5));

        // Write the number in the pipe
        printf("Child %d: send a value\n", num);
        if(write(out, &num, sizeof(int)) == -1) {
            fprintf(stderr, "Child %d: error during writing in the pipe", num);
            perror("");
            exit(EXIT_FAILURE);
        }
    }

    exit(EXIT_SUCCESS);
}

/**
 * Handler for the SIGINT signal.
 * @param signum the number of the received signal
 */
void handler(int signum) {
    stop = 1;
}

/**
 * Main function.
 * @param argc the number of arguments
 * @param argv the arguments (name of the program, number of children)
 * @return EXIT_FAILURE ou EXIT_SUCCESS
 */
int main(int argc, char *argv[]) {
    int *pipes;
    int children_number, i, j, max_fd, value, nb;
    pid_t *pids;
    struct sigaction action;
    fd_set set;
    sigset_t signals;

    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s nb\n", argv[0]);
        fprintf(stderr, "\tWhere :\n");
        fprintf(stderr, "\t\tnb: the number of children (between 2 and 10)\n");
        exit(EXIT_FAILURE);
    }

    // Get and check the children number
    children_number = atoi(argv[1]);
    if((children_number < 2) || (children_number > 10)) {
        fprintf(stderr, "You must specify a number of children between 2 and 10 (here %d)\n", children_number);
        exit(EXIT_FAILURE);
    }

    // Allocate arrays for pipes and children pids
    if((pipes = malloc(sizeof(int) * 2 * children_number)) == NULL) {
        perror("Error allocating array (1)");
        exit(EXIT_FAILURE);
    }
    if((pids = malloc(sizeof(pid_t) * children_number)) == NULL) {
        perror("Error allocating array (1)");
        exit(EXIT_FAILURE);
    }

    // Create pipes and children
    for(i = 0; i < children_number; i++) {
        // Create pipe for the child
        if(pipe(&pipes[i * 2]) == -1) {
            fprintf(stderr, "Error creating pipe %d", i);
            perror("");
            exit(EXIT_FAILURE);
        }

        // Create son
        if((pids[i] = fork()) == -1) {
            fprintf(stderr, "Error creating child %d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        
        if(pids[i] == 0) {
            // Close read pipes
            for(j = 0; j <= i; j++) {
                if(close(pipes[j * 2]) == -1) {
                    fprintf(stderr, "Child %d: error closing read pipe %d", i, j);
                    perror("");
                    exit(EXIT_FAILURE);
                }
            }

            // Child function
            child(i, pipes[i * 2 + 1]);
        }
        else {
            // Close current write pipe
            if(close(pipes[i * 2 + 1]) == -1) {
                fprintf(stderr, "Father: error closing write pipe %d", i);
                perror("");
                exit(EXIT_FAILURE);
            }
        }
    }
  
    // Specify a handler for SIGINT signal
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning handler");
        exit(EXIT_FAILURE);
    }

    // Main loop
    sigemptyset(&signals);
    while(stop == 0) {
        // Céeation de l'ensemble des descripteurs
        FD_ZERO(&set);
        max_fd = 0;
        FD_SET(STDIN_FILENO, &set);
        for(i = 0; i < children_number; i++) {
            FD_SET(pipes[i * 2], &set);
            if(pipes[i * 2] > max_fd)
                max_fd = pipes[i * 2];
        }
        max_fd++; // We must specify the maximum descriptor number + 1

        // Wait for data
        printf("Father: wait for values (CRTL + C to stop)\n");
        if((nb = pselect(max_fd, &set, NULL, NULL, NULL, &signals)) == -1) {
            if(errno != EINTR) {
                perror("Error waiting for events on file descriptors");
                exit(EXIT_FAILURE);
            }
        }

        // Check all pipes
        if(stop == 0) {
            printf("Data in %d pipe(s).\n", nb);
            for(i = 0; i < children_number; i++) {
                if(FD_ISSET(pipes[i * 2], &set)) {
                    if(read(pipes[i * 2], &value, sizeof(int)) == -1) {
                        fprintf(stderr, "Father: error on reading in pipe %d", i);
                        perror("");
                        exit(EXIT_FAILURE);
                    }
                    printf("Father: read %d from pipe %d\n", value, i);
                }
            }
        }
    }

    printf("Father: signal received, stopping children.\n");

    // Stop children
    for(i = 0; i < children_number; i++) {
        // Send a signal
        if(kill(pids[i], SIGINT) == -1) {
            fprintf(stderr, "Error sending signal to child %d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Father: signal sent to son %d\n", i);

        // Wait for the child end
        if(waitpid(pids[i], NULL, 0) == -1) {
            fprintf(stderr, "Error waiting for child %d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Father: child %d stopped.\n", i);
    }

    // Close pipes
    for(i = 0; i < children_number; i++) {
        if(close(pipes[i * 2]) == -1) {
            fprintf(stderr, "Error closing read pipe %d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
    }
    
    // Free memory
    free(pids);
    free(pipes);

    return EXIT_SUCCESS;
}