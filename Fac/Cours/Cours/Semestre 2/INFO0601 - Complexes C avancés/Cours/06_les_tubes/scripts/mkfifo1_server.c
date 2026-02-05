/**
 * Creation of a named pipe and communication between the server and client
 * programs. The server sends 5 integers to the client.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
 
#define PIPE_NAME "/tmp/mypipe"
 
int main() {
    int fd, i;
    
    if(mkfifo(PIPE_NAME, S_IRUSR | S_IWUSR) == -1) {
        fprintf(stderr, "Error creating named pipe '%s'", PIPE_NAME);
        perror("");
        exit(EXIT_FAILURE);
    }
    
    printf("Waiting for client...\n");
    if((fd = open(PIPE_NAME, O_WRONLY)) == -1) {
        perror("Error opening pipe");
        exit(EXIT_FAILURE);
    }
    printf("The pipe is open.\n");
    
    for(i = 0; i < 5; i++) {
        if(write(fd, &i, sizeof(int)) == -1) {
            perror("Error writing integers in pipe");
            exit(EXIT_FAILURE);
        }
    }
    printf("Integers sent.\n");
    
    if(close(fd) == -1) {
        perror("Error closing pipe");
        exit(EXIT_FAILURE);
    }
    
    if(unlink(PIPE_NAME) == -1) {
        perror("Error deleting pipe");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}