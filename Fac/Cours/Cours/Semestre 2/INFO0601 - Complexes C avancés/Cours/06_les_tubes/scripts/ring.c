/**
 * Example of a ring communication with named pipes.
 * This program must be launched 5 times by specifying a number, starting from 0:
 * ./ring 0, ./ring 1, ./ring 2, /ring 3, /ring 4
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

#define PIPE_NAME "/tmp/pipe_"
#define PROG_NB  5

void termination() {
    int i;
    char name[256];

    // Deleting pipes
    for(i = 0; i < PROG_NB; i++) {
        sprintf(name, "%s%d", PIPE_NAME, i);
        if(unlink(name) == -1) {
            if(errno != ENOENT) {
                fprintf(stderr, "Error deleting pipe '%s'", name);
                perror(" ");
                exit(EXIT_FAILURE);
            }
        }
    }
}

int main(int argc, char *argv[]) {
    int n, i;
    int in, out;
    char name[256];

    // Checking arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s n with n>=0 and n<%d\n", argv[0], PROG_NB);
        exit(EXIT_FAILURE);
    }
    n = atoi(argv[1]);
    if((n < 0) || (n >= PROG_NB)) {
        fprintf(stderr, "The argument must be in [0; %d]\n", PROG_NB - 1);
        exit(EXIT_FAILURE);
    }

    if(n == 0) {
        // Register termination function
        if(atexit(termination) == -1) {
            perror("Error registering termination function");
            exit(EXIT_FAILURE);
        }
    
        // Create pipes
        for(i = 0; i < PROG_NB; i++) {
            sprintf(name, "%s%d", PIPE_NAME, i);
            if(mkfifo(name, S_IRUSR | S_IWUSR) == -1) {
                if(errno != EEXIST) {
                    fprintf(stderr, "Error creating pipe '%s'", name);
                    perror(" ");
                    exit(EXIT_FAILURE);
                }
                else
                    fprintf(stderr, "The pipe '%s' already exists.\n", name);
            }
        }
    }
    else {
        printf("Process #%d: waiting for the pipes creation.\n", n);
        sleep(1);
    }

    // Open pipes
    if(n % 2 == 0) {
        sprintf(name, "%s%d", PIPE_NAME, (n + 1) % PROG_NB);
        printf("Process #%d: open pipe '%s' for writing.\n", n, name);
        if((out = open(name, O_WRONLY)) == -1) {
            fprintf(stderr, "Process #%d: error opening pipe '%s'", n, name);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: pipe '%s' is open for writing.\n", n, name);

        sprintf(name, "%s%d", PIPE_NAME, n);
        printf("Process #%d: open pipe '%s' for reading.\n", n, name);
        if((in = open(name, O_RDONLY)) == -1) {
            fprintf(stderr, "Process #%d: error opening piep '%s'", n, name);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: pipe '%s' is open for reading.\n", n, name);
    }
    else {
        sprintf(name, "%s%d", PIPE_NAME, n);
        printf("Process #%d: open pipe '%s' for reading.\n", n, name);
        if((in = open(name, O_RDONLY)) == -1) {
            fprintf(stderr, "Process #%d: error opening pipe '%s'", n, name);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: pipe '%s' is open for reading.\n", n, name);

        sprintf(name, "%s%d", PIPE_NAME, (n + 1) % PROG_NB);
        printf("Process #%d: open pipe '%s' for writing.\n", n, name);
        if((out = open(name, O_WRONLY)) == -1) {
            fprintf(stderr, "Process #%d: error opening pipe '%s'", n, name);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: pipe '%s' is open for writing.\n", n, name);
    }
    printf("Process #%d : ready.\n", n);

    // Send the first integer
    if(n == 0) {
        i = 0;
        if(write(out, &i, sizeof(int)) == -1) {
            fprintf(stderr, "Process #%d: error writing integer", n);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: integer %d sent.\n", n, i);
    }

    // Waiting for an integer
    if(read(in, &i, sizeof(int)) == -1) {
        fprintf(stderr, "Process #%d: error reading integer", n);
        perror(" ");
        exit(EXIT_FAILURE);
    }
    printf("Process #%d: integer %d read.\n", n, i);

    // Return the value
    if(n != 0) {
        i++;
        if(write(out, &i, sizeof(int)) == -1) {
            fprintf(stderr, "Process #%d: error writing integer", n);
            perror(" ");
            exit(EXIT_FAILURE);
        }
        printf("Process #%d: integer %d sent.\n", n, i);
    }

    printf("Process #%d: stop.\n", n);
    
    return EXIT_SUCCESS;
}
