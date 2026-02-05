/**
 * This program simulates the use of a shared lock variable to manage the
 * mutual exclusion between two processes.
 * - We use a shared memory segment for the variable
 * - A pipe is used to check when children enter or leave the critical section
 * - A SIGINT signal (CRTL + C) is used to stop the execution 
 * We observe some errors at execution: a process enters in critical section
 * when the other process is already in critical section.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/wait.h>

#define CLE 1056

int stop = 0;

/**
 * Handler for SIGINT signal.
 * @param signum the received signal number
 */
void handler(int signum) {
    stop = 1;
}

/**
 * Generate a random integer in [a;b]
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int _random(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Code for the children.
 * @param num the child number
 * @param out the file descriptor for output
 * @param lock the lock variable
 */
void child(int num, int out, int *lock) {    
    // Main loop
    while(stop == 0) {
        // Infinite loop
        while(*lock == 1);
        sleep(_random(1, 2)); // to increase the chance of being interrupted
        *lock = 1;
        
        // Enter critical section
        if(write(out, &num, sizeof(int)) == -1) {
            fprintf(stderr, "Child #%d, error writting in pipe:", num);
            perror("");
            exit(EXIT_FAILURE);
        }
        sleep(_random(1, 2)); // to increase the chance of being interrupted
        
        // Leave critical section
        *lock = 0;
        if(write(out, &num, sizeof(int)) == -1) {
            fprintf(stderr, "Child #%d, error writting in pipe:", num);
            perror("");
            exit(EXIT_FAILURE);
        }
    }
    fprintf(stderr, "Child #%d, stopped\n", num);
    
    // Close the write pipe
    if(close(out) == -1) {
        fprintf(stderr, "Child #%d, error closing write pipe:", num);
        perror("");
        exit(EXIT_FAILURE);
    }    
    
    // Detach the shared memory segment
    if(shmdt(lock) == -1) {
        fprintf(stderr, "Child #%d, error detaching segment:", num);
        exit(EXIT_FAILURE);
    }
    
    exit(EXIT_FAILURE);
}

int main() {
    int shmid, i;
    int *lock;
    int children[2], _pipe[2];
    pid_t pids[2];
    struct sigaction action;

    // Create the shared memory segment
    if((shmid = shmget(CLE, sizeof(int), S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        perror("Father: error creating shared memory segment");
        exit(EXIT_FAILURE);
    }
    printf("Father: shared memory segment created\n");
    
    // Initialize the shared memory segment
    if((lock = shmat(shmid, NULL, 0)) == (void*)-1) {
        perror("Father: error attaching segment");
        exit(EXIT_FAILURE);
    }
    *lock = 0;
    printf("Father: shared memory segment initialized\n");
    
    // Creating pipe
    if(pipe(_pipe) == -1) {
        perror("Father: error creating pipe");
        exit(EXIT_FAILURE);
    }
    
    // Creating children
    for(i = 0; i < 2; i++) {
        if((pids[i] = fork()) == 1) {
            perror("Father: error creating child");
            exit(EXIT_FAILURE);
        }
        if(pids[i] == 0) {
            if(close(_pipe[0]) == -1) {
                fprintf(stderr, "Child #%d: error closing read pipe", i);
                perror("");
                exit(EXIT_FAILURE);
            }
            child(i, _pipe[1], lock);
        }
        children[i] = 0;
    }
    
    // Specify the SIGINT handler
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning handler");
        exit(EXIT_FAILURE);
    }       
    
    // Detach the shared memory segment
    if(shmdt(lock) == -1) {
        perror("Father: error detaching segment");
        exit(EXIT_FAILURE);
    }    
    
    // Close the write pipe
    if(close(_pipe[1]) == -1) {
        fprintf(stderr, "Father: error closing write pipe");
        perror("");
        exit(EXIT_FAILURE);
    }    
    
    // Father's main loop
    printf("Father: ready\n");
    while(stop == 0) {
        if(read(_pipe[0], &i, sizeof(int)) == -1) {
            if(errno != EINTR) {
                fprintf(stderr, "Father: error reading in pipe");
                perror("");
                exit(EXIT_FAILURE);
            }
        }
        else {
            if(children[i] == 1)
                children[i] = 0;
            else {
                if(children[1 - i] == 1) {
                    // Other child is already in critical section
                    printf("Father: \x1B[31m[ERROR]\x1B[0m child #%d enters in critical section\n", i);
                }
                children[i] = 1;
            }
        }
    }
    printf("Father: stopped\n");
    
    // Kill children
    for(i = 0; i < 2; i++) {
        if(kill(pids[i], SIGINT) == -1) {
            fprintf(stderr, "Father: error killing child #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
    }    
    
    // Delete the shared memory segment
    if(shmctl(shmid, IPC_RMID, 0) == -1) {
        perror("Father: erreur deleting shared memory segment");
        exit(EXIT_FAILURE);
    }
    
    // Close the read pipe
    if(close(_pipe[0]) == -1) {
        fprintf(stderr, "Father: error closing read pipe");
        perror("");
        exit(EXIT_FAILURE);
    }   
    
    // Wait for children end
    printf("Father: waiting for children end\n");
    for(i = 0; i < 2; i++) {
        if((wait(NULL)) == 1) {
            perror("Father: error waiting child");
            exit(EXIT_FAILURE);
        }
    }
    printf("Father: all children are stopped\n");

    return EXIT_SUCCESS;
}