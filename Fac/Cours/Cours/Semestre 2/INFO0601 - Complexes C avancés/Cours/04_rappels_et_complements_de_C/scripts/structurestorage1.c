/**
 * Store a structure with static fields.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

typedef struct {
  char lastname[256];
  char firstname[256];
  int age;
} person_t;

int main() {
    /* Écriture */
    person_t p = { "Smith", "John", 30 }, p2;
    int fd;
      
    if((fd = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    if(write(fd, &p, sizeof(person_t)) == -1) {
        perror("Error writing structure");
        exit(EXIT_FAILURE);
    }

    if(close(fd) == -1) {
        perror("Error closing file (1)");
        exit(EXIT_FAILURE);
    }

    if((fd = open("toto.bin", O_RDONLY, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error opening file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    if(read(fd, &p2, sizeof(person_t)) == -1) {
        perror("Error reading structure");
        exit(EXIT_FAILURE);
    }    
    printf("%s %s (%d year(s) old)\n", p2.firstname, p2.lastname, p2.age);

    if(close(fd) == -1) {
        perror("Error closing file (2)");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}