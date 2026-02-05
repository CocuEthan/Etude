/**
 * Using `fork` to create a son process.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid;

    if((pid = fork()) == -1) {
        perror("Error creating child process");
        exit(EXIT_FAILURE);
    }
  
    if(pid > 0) {
        printf("This is executed by father process.\n");
      
        if(wait(NULL) == -1) {
            perror("Error waiting child process end");
            exit(EXIT_FAILURE);
        }
    }
    else {
        printf("This is executed by child process.\n");
    }
    printf("This is executed by father and child processes.\n");
    
    return EXIT_SUCCESS;
}