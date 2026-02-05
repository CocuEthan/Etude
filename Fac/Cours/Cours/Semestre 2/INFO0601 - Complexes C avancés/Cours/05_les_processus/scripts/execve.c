/**
 * Program that illustrates how to run a program using `execve`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

void execution(char *argve[]) {
    char *arguments[4] = { "./helloworld", "Hello", "everybody", NULL };

    printf("I launch the program...\n");
    if(execve("./helloworld", arguments, argve) == -1) {
        perror("Error launching program");
    }
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[], char *argve[]) {
    pid_t pid;

    if((pid = fork()) == -1) {
        perror("Error creating child process");
        exit(EXIT_FAILURE);
    }
    if(pid == 0)
        execution(argve);

    if(wait(NULL) == -1) {
        perror("Error waiting child process end");
        exit(EXIT_FAILURE);
    }
    
    printf("Program stopped.\n");

    return EXIT_SUCCESS;
}