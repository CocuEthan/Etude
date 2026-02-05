/**
 * Write a static string into a binary file and read it.
 * Example of writing size of the string then the string.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define SIZE 10

int main() {
    char str1[SIZE] = "Cool";
    int fd1;
    size_t size;
      
    /* Write */
    if((fd1 = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    size = sizeof(char) * (strlen(str1) + 1);
    if(write(fd1, &size, sizeof(size_t)) == -1) {
        perror("Error saving size");
        exit(EXIT_FAILURE);
    }    
    if(write(fd1, str1, size) == -1) {
        perror("Error saving string");
        exit(EXIT_FAILURE);
    }

    if(close(fd1) == -1) {
        perror("Error closing file (1)");
        exit(EXIT_FAILURE);
    }
    printf("Write: '%ld' and '%s'\n", size, str1);

    /* Read */
    char* str2;
    int fd2;

    if((fd2 = open("toto.bin", O_RDONLY, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error opening file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    if(read(fd2, &size, sizeof(size_t)) == -1) {
        perror("Error reading size");
        exit(EXIT_FAILURE);
    }
    
    if((str2 = malloc(sizeof(char) * SIZE)) == NULL) {
        perror("Error allocating string");
        exit(EXIT_FAILURE);
    }
    
    if(read(fd2, str2, sizeof(char) * SIZE) == -1) {
        perror("Error reading string");
        exit(EXIT_FAILURE);
    }    
    printf("Read: '%ld' and '%s'\n", size, str2);

    free(str2);

    if(close(fd2) == -1) {
        perror("Error closing file (2)");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}