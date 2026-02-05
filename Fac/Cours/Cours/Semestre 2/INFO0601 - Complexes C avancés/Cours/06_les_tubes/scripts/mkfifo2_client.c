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
    int fd1, fd2, i;
        
    if((fd1 = open(PIPE_NAME_1, O_RDONLY)) == -1) {
        perror("Error opening pipe #1");
        exit(EXIT_FAILURE);
    }
    if((fd2 = open(PIPE_NAME_2, O_WRONLY)) == -1) {
        perror("Error opening pipe #2");
        exit(EXIT_FAILURE);
    }
    
    if(read(fd1, &i, sizeof(int)) == -1) {
        perror("Error reading integer from pipe #1");
        exit(EXIT_FAILURE);
    }
    printf("Integer read = %d\n", i);
    i *= 2;
    
    if(write(fd2, &i, sizeof(int)) == -1) {
        perror("Error writing integer in pipe #2");
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
    
    return EXIT_SUCCESS;
}