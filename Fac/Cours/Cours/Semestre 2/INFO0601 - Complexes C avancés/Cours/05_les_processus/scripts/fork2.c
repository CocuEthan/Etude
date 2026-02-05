/**
 * Illustration of the independence between the memory of a process and
 * that of its child.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int global = 1;

int main() {
    pid_t pid;
    int i = 1;

    if((pid = fork()) == -1) {
        perror("Error creating child process");
        exit(EXIT_FAILURE);
    }
  
    if(pid == 0) {
        global++;
        i++;
    }
    else {
        global--;
        i--;
    }
    printf("PID=%d, global=%d, i=%d\n", getpid(), global, i);
    
    return EXIT_SUCCESS;
}