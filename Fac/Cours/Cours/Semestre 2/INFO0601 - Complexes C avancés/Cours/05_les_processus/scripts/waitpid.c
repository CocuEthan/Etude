/**
 * Program that shows how to wait for a child to finish and how to
 * retrieve its status using `waitpid`
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
    pid_t pid[2];
    int i, statut;

    // Create two childs
    for(i = 0; i < 2; i++) {
        if((pid[i] = fork()) == -1) {
            perror("Error creating child process");
            exit(EXIT_FAILURE);
        }
      
        if(pid[i] == 0)
            child();
    }
    
    printf("I'm in the father and I wait for the child processes end in order.\n");
  
    // Wait child processes end
    for(i = 0; i < 2; i++) {
        if(waitpid(pid[i], &statut, 0) == -1) {
            perror("Error waiting child process end");
            exit(EXIT_FAILURE);
        }
        if(WIFEXITED(statut))
            printf("Child %d ended; return value = %d.\n", (i+1), WEXITSTATUS(statut));
        else
            printf("Child %d ended abnormally.\n", (i+1));
    }  
    
    return EXIT_SUCCESS;
}