/**
 * Use `dup2` to create a redirection between 2 programs.
 * A pipe is created between a father and its child. The child output pipe
 * is associated to the standard output, then `ls -l` is run. The father input
 * pipe is associated to the standard enty, then `wc -l` is run.
 * This program is equivalent to the command 'ls -l | wc -l'.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

#define PIPE_READ  0
#define PIPE_WRITE 1

void child(int out) {
    char *arguments[3] = { "ls", "-l", NULL };

    // Overwriting of output descriptors (output and error output)
    if(dup2(out, STDOUT_FILENO) == -1) {
        perror("Child: error duplicating the descriptor (1)");
        exit(EXIT_FAILURE);
    }
    if(dup2(out, STDERR_FILENO) == -1) {
        perror("Child: error duplicating the descriptor (2)");
        exit(EXIT_FAILURE);
    } 
    
    // Close pipe for writing
    if(close(out) == -1) {
        perror("Child: error closing pipe for writing");
        exit(EXIT_FAILURE);
    }

    // Run 'ls -l'
    if(execve("/bin/ls", arguments, NULL) == -1) {
        perror("Child: error executing `ls`");
    }
    
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
    int _pipe[2];
    pid_t pid;
    char *arguments[3] = { "wc", "-l", NULL };

    // Create pipe
    if(pipe(_pipe) == -1) {
        perror("Father: error creating pipe");
        exit(EXIT_FAILURE);
    }

    // Create child
    if((pid = fork()) == -1) {
        perror("Father: error creating child");
        exit(EXIT_FAILURE);
    }
    if(pid == 0) {
        // Close pipe for reading
        if(close(_pipe[PIPE_READ]) == -1) {
            perror("Child: error closing pipe for reading");
            exit(EXIT_FAILURE);
        }
        child(_pipe[PIPE_WRITE]);
    }

    // Close pipe for writing
    if(close(_pipe[PIPE_WRITE]) == -1) {
        perror("Father: error closing pipe for writing");
        exit(EXIT_FAILURE);
    }

    // Overwriting of input descriptor
    if(dup2(_pipe[PIPE_READ], STDIN_FILENO) == -1) {
        perror("Father: error duplicating the descriptor");
        exit(EXIT_FAILURE);
    }

    // Close pipe for reading
    if(close(_pipe[PIPE_READ]) == -1) {
        perror("Father: error closing pipe for reading");
        exit(EXIT_FAILURE);
    }

    // Run `wc -l`
    if(execve("/usr/bin/wc", arguments, NULL) == -1) {
        perror("Father: error executing `wc`");
    }

    return EXIT_FAILURE;
}