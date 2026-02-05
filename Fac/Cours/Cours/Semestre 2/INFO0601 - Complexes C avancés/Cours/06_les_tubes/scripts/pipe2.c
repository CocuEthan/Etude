/**
 * * Create of a bidirectional communication pipe between a process and
 * its child. The father sends an integer and the child replies with its
 * integer mutiplied by 2. The program stops after 5 iterations.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
 
#define PIPE_READ  0
#define PIPE_WRITE 1

/**
 * Child main.
 * @param f_c the father-to-child pipe
 * @param c_f the child-to-father pipe
 */
void child(int f_c[2], int c_f[2]) {
    int i, tmp;

    if(close(f_c[PIPE_WRITE]) == -1) {
        perror("Child: error closing the write descriptor pipe (1)");
        exit(EXIT_FAILURE);
    }
    if(close(c_f[PIPE_READ]) == -1) {
        perror("Child: error closing the read descriptor pipe (1)");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        if(read(f_c[PIPE_READ], &tmp, sizeof(int)) == -1) {
            fprintf(stderr, "Child: error reading integer #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Child:  integer read = %d\n", tmp);
        tmp *= 2;
        if(write(c_f[PIPE_WRITE], &tmp, sizeof(int)) == -1) {
            fprintf(stderr, "Child: error writing integer #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Child:  integer sent = %d\n", tmp);
    }
    
    if(close(c_f[PIPE_WRITE]) == -1) {
        perror("Child: error closing the write descriptor pipe (2)");
        exit(EXIT_FAILURE);
    }
    if(close(f_c[PIPE_READ]) == -1) {
        perror("Child: error closing the read descriptor pipe (2)");
        exit(EXIT_FAILURE);
    }
    
    exit(EXIT_SUCCESS);
}

int main() {
    pid_t pid;
    int f_c[2], c_f[2], i, tmp = 1;
    
    if(pipe(f_c) == -1) {
        perror("Error creating father-to-child pipe");
        exit(EXIT_FAILURE);
    }
    if(pipe(c_f) == -1) {
        perror("Error creating child-to-father pipe");
        exit(EXIT_FAILURE);
    }
    
    if((pid = fork()) == -1) {
        perror("Error creating son");
        exit(EXIT_FAILURE);
    }

    if(pid == 0)
        child(f_c, c_f);
    
    if(close(c_f[PIPE_WRITE]) == -1) {
        perror("Father: error closing the write descriptor pipe (1)");
        exit(EXIT_FAILURE);
    }
    if(close(f_c[PIPE_READ]) == -1) {
        perror("Father: error closing the read descriptor pipe (1)");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        if(write(f_c[PIPE_WRITE], &tmp, sizeof(int)) == -1) {
            fprintf(stderr, "Father: error writing integer #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Father: integer sent = %d\n", tmp);
        
        if(read(c_f[PIPE_READ], &tmp, sizeof(int)) == -1) {
            fprintf(stderr, "Father: error reading integer #%d", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Father: integer read = %d\n", tmp);
    }
    
    if(close(f_c[PIPE_WRITE]) == -1) {
        perror("Father: error closing the write descriptor pipe (2)");
        exit(EXIT_FAILURE);
    }
    if(close(c_f[PIPE_READ]) == -1) {
        perror("Father: error closing the read descriptor pipe (2)");
        exit(EXIT_FAILURE);
    }
    
    if(wait(NULL) == -1) {
        perror("Father: error waiting child");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}