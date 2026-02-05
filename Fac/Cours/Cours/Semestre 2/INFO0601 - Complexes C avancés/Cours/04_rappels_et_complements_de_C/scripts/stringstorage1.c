/**
 * Write a static string into a binary file and read it.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

#define SIZE 10

int main() {
    char str1[SIZE] = "Cool";
    int fd1;
      
    /* Writing */
    if((fd1 = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    if(write(fd1, str1, sizeof(char) * SIZE) == -1) {
        perror("Error writing string");
        exit(EXIT_FAILURE);
    }

    if(close(fd1) == -1) {
        perror("Error closing file (1)");
        exit(EXIT_FAILURE);
    }
    printf("Write: '%s'\n", str1);

    /* Reading */
    char str2[SIZE];
    int fd2;

    if((fd2 = open("toto.bin", O_RDONLY, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error opening file 'toto.bin' ");
        exit(EXIT_FAILURE);
    }

    if(read(fd2, str2, sizeof(char) * SIZE) == -1) {
        perror("Error reading string");
        exit(EXIT_FAILURE);
    }    
    printf("Read: '%s'\n", str2);

    if(close(fd2) == -1) {
        perror("Error closing file (2)");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}