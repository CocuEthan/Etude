/**
 * Creation of two named pipes and two-way communication between the server and
 * client programs. The server sends 5 integers to the client and the client
 * returns them.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
 
#define PIPE_NAME_1 "/tmp/mypipe1"
#define PIPE_NAME_2 "/tmp/mypipe2"
 
int main() {
    int fd1, fd2, i = 5;
    
    if(mkfifo(PIPE_NAME_1, S_IRUSR | S_IWUSR) == -1) {
        fprintf(stderr, "Error creating named pipe '%s'", PIPE_NAME_1);
        perror("");
        exit(EXIT_FAILURE);
    }
    if(mkfifo(PIPE_NAME_2, S_IRUSR | S_IWUSR) == -1) {
        fprintf(stderr, "Error creating named pipe '%s'", PIPE_NAME_2);
        perror("");
        exit(EXIT_FAILURE);
    }
    
    printf("Waiting for client...\n");
    if((fd1 = open(PIPE_NAME_1, O_WRONLY)) == -1) {
        perror("Error opening pipe #1");
        exit(EXIT_FAILURE);
    }
    if((fd2 = open(PIPE_NAME_2, O_RDONLY)) == -1) {
        perror("Error opening pipe #2");
        exit(EXIT_FAILURE);
    }
    printf("The pipes are open.\n");
    
    if(write(fd1, &i, sizeof(int)) == -1) {
        perror("Error writing integer in pipe #1");
        exit(EXIT_FAILURE);
    }
    printf("Integer sent = %d\n", i);

    if(read(fd2, &i, sizeof(int)) == -1) {
        perror("Error reading integer from pipe #2");
        exit(EXIT_FAILURE);
    }
    printf("Integer sent = %d\n", i);
    
    if(close(fd1) == -1) {
        perror("Error closing pipe #1");
        exit(EXIT_FAILURE);
    }
    if(close(fd2) == -1) {
        perror("Error closing pipe #2");
        exit(EXIT_FAILURE);
    }
    
    if(unlink(PIPE_NAME_1) == -1) {
        perror("Error deleting pipe #1");
        exit(EXIT_FAILURE);
    }
    if(unlink(PIPE_NAME_2) == -1) {
        perror("Error deleting pipe #2");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}