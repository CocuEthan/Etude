/**
 * Store a structure with dynamic fields.
 * It shows two BAD METHODS!
 * Type "more toto.bin" to see the problem.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

typedef struct {
  char *lastname;
  char *firstname;
  int age;
} person_t;

int main() {
    person_t p = { "Norris", "Chuck", 81 };
    int fd, i;
      
    // Save structure
    if((fd = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }
    
    printf("1) for method 1 or 2) for method 2: ");
    if(scanf("%d", &i) != 1) {
        fprintf(stderr, "Error reading choice\n");
        exit(EXIT_FAILURE);
    }

    if(i == 1) {
        // Write structure (not good...)
        if(write(fd, &p, sizeof(person_t)) == -1) {
            perror("Error saving structure (1)");
            exit(EXIT_FAILURE);
        }
    }
    else {    
        // Write structure (still not good...)
        if(write(fd, &p, sizeof(person_t) + (strlen(p.lastname) + strlen(p.firstname) + 2) * sizeof(char) + sizeof(int)) == -1) {
            perror("Error saving structure (2)");
            exit(EXIT_FAILURE);
        }
    }

    // Close file
    if(close(fd) == -1) {
        perror("Error closing file");
        exit(EXIT_FAILURE);
    }
    printf("Structure saved (or not...).\n");
    
    return EXIT_SUCCESS;
}