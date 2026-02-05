/**
 * Creation of a named pipe and communication between the server and client
 * programs. The server sends 5 integers to the client.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

#define PIPE_NAME "/tmp/mypipe"
 
int main() {
    int fd, i, tab[5];
        
    if((fd = open(PIPE_NAME, O_RDONLY)) == -1) {
        perror("Error opening pipe");
        exit(EXIT_FAILURE);
    }
    
    if(read(fd, tab, sizeof(int) * 5) == -1) {
        perror("Error reading integers from pipe");
        exit(EXIT_FAILURE);
    }
    
    printf("Read: ");
    for(i = 0; i < 5; i++)
        printf("%d ", i);
    printf("\n");    
    
    if(close(fd) == -1) {
        perror("Error closing pipe");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}