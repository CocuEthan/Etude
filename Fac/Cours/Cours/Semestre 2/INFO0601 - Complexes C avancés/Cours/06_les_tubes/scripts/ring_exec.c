/**
 * Runs 5 times the ring program.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define NB_PROG  5

int main(int argc, char **argv) {
    int i;
    pid_t pid;
    char *arguments[3] = { "ring", NULL, NULL };

    // Runs programs
    for(i = 0; i < 5; i++) {
        if((pid = fork()) == -1) {
            fprintf(stderr, "Error creating child #%d", i);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        if(pid == 0) {
            arguments[1] = (char*)malloc(sizeof(char) * 256);
            sprintf(arguments[1], "%d", i);
            if(execve("ring", arguments, NULL) == -1) {
                perror("Error runs 'ring' program");
            }
            exit(EXIT_FAILURE);
        }
    }
    printf("%s: children created.\n", argv[0]);

    // Waiting for end of children
    for(i = 0; i < 5; i++) {
        if(wait(NULL) == -1) {
            perror("Error waiting for child end");
            exit(EXIT_FAILURE);
        }
    }
    printf("%s: all children stopped.\n", argv[0]);

    return EXIT_SUCCESS;
}