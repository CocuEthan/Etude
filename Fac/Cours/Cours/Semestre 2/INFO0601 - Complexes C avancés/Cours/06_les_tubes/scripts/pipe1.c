/**
 * Create of a pipe between a process and its child. The child writes 5
 * integers that the father reads.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
 
void child(int _pipe[2]) {
    int i;

    if(close(_pipe[0]) == -1) {
        perror("Child: error while closing the read descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        if(write(_pipe[1], &i, sizeof(int)) == -1) {
            fprintf(stderr, "Child: error writing integer #%d ", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Child: integer sent = %d\n", i);
    }
    
    if(close(_pipe[1]) == -1) {
        perror("Child: error while closing the write descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    exit(EXIT_SUCCESS);
}

int main() {
    pid_t pid;
    int _pipe[2], i, tmp;
    
    if(pipe(_pipe) == -1) {
        perror("Error creating pipe");
        exit(EXIT_FAILURE);
    }
    
    if((pid = fork()) == -1) {
        perror("Error creating child process");
        exit(EXIT_FAILURE);
    }

    if(pid == 0)
        child(_pipe);
    
    if(close(_pipe[1]) == -1) {
        perror("Father: error while closing the write descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        if(read(_pipe[0], &tmp, sizeof(int)) == -1) {
            fprintf(stderr, "Father: error when reading integer #%i", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Father: integer read = %d\n", tmp);
        sleep(1);
    }
    
    if(close(_pipe[0]) == -1) {
        perror("Father: error while closing the read descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    if(wait(NULL) == -1) {
        perror("Father: error waiting child");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}