/**
 * Using `fcntl` to change file descriptor attributes. The father
 * (actively) waits for the child to send integers.
 * WARNING: it is NOT a good pratice! It only illustrates how to use `fcntl`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <errno.h>
#include <time.h>

int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}
 
void child(int _pipe[2]) {
    int i;
    
    srand(time(NULL) + getpid());

    if(close(_pipe[0]) == -1) {
        perror("Child: error closing the read descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        sleep(random_integer(1, 5));
        if(write(_pipe[1], &i, sizeof(int)) == -1) {
            fprintf(stderr, "Child: error writing integer #%d ", i);
            perror("");
            exit(EXIT_FAILURE);
        }
        printf("Child: integer sent = %d\n", i);
    }
    
    if(close(_pipe[1]) == -1) {
        perror("Child: error closing the write descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    exit(EXIT_SUCCESS);
}

int main() {
    pid_t pid;
    int _pipe[2], i, tmp, attributes, res;
    
    if(pipe(_pipe) == -1) {
        perror("Error creating pipe");
        exit(EXIT_FAILURE);
    }
    
    if((pid = fork()) == -1) {
        perror("Error creating child");
        exit(EXIT_FAILURE);
    }

    if(pid == 0)
        child(_pipe);
    
    if(close(_pipe[1]) == -1) {
        perror("Father: error closing the write descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    if((attributes = fcntl(_pipe[0], F_GETFL)) == -1) {
        perror("Father: error getting descriptor attributes");
        exit(EXIT_FAILURE);
    }
    if(fcntl(_pipe[0], F_SETFL, attributes | O_NONBLOCK) == -1) {
        perror("Father: error setting descriptor attributes");
        exit(EXIT_FAILURE);
    }
    
    for(i = 0; i < 5; i++) {
        res = read(_pipe[0], &tmp, sizeof(int));
        while((res == -1) && (errno == EAGAIN)) {
            printf("I have not received anything yet...\n");
            sleep(1);
            res = read(_pipe[0], &tmp, sizeof(int));
        }
        if((res == -1) && (errno != EAGAIN)) {
            perror("Father: error reading integer");
            exit(EXIT_FAILURE);
        }
        printf("Father: integer read = %d\n", tmp);
    }
    
    if(close(_pipe[0]) == -1) {
        perror("Father: error closing the read descriptor pipe");
        exit(EXIT_FAILURE);
    }
    
    if(wait(NULL) == -1) {
        perror("Father: error waiting child");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}