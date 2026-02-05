/**
 * Write a static string into a binary file and read it.
 * Example of reading character by character: TO DO USE!
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
      
    /* Write */
    if((fd1 = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    if(write(fd1, str1, sizeof(char) * (strlen(str1) + 1)) == -1) {
        perror("Error writing string");
        exit(EXIT_FAILURE);
    }

    if(close(fd1) == -1) {
        perror("Error closing file (1)");
        exit(EXIT_FAILURE);
    }
    printf("Write: '%s'\n", str1);

    /* Read */
    char str2[SIZE];
    int fd2;

    if((fd2 = open("toto.bin", O_RDONLY, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error opening file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    int i = 0;
    while((read(fd2, &str2[i], sizeof(char)) == sizeof(char)) && str2[i] != '\0')
        i++;
    printf("Read: '%s'\n", str2);

    if(close(fd2) == -1) {
        perror("Error closing file (2)");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}