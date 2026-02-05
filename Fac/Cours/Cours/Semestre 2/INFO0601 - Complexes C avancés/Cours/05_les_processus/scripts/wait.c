/**
 * Program that shows how to wait for a child to finish and how to
 * retrieve its status using `wait`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

void child() {
    printf("I'm in the child.\n");
    exit(EXIT_FAILURE);
}

int main() {
    pid_t pid;
    int statut;

    if((pid = fork()) == -1) {
        perror("Error creating child process");
        exit(EXIT_FAILURE);
    }
  
    if(pid == 0)
        child();
    
    printf("I'm in the father and I wait for the child end.\n");
  
    if(wait(&statut) == -1) {
        perror("Error waiting child process end");
        exit(EXIT_FAILURE);
    }
    if(WIFEXITED(statut))
        printf("The child ended; return value = %d.\n", WEXITSTATUS(statut));
    else
        printf("The child ended abnormally.\n");
    
    return EXIT_SUCCESS;
}