/**
 * Store a structure with dynamic fields.
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
    person_t *p; // Here, the pointer isn't necessary, but it's for the example
    int fd;
    char buffer[256];
    char c;
    size_t size;

    // Structure allocation
    if((p = (person_t*)malloc(sizeof(person_t))) == NULL) {
        perror("Error allocating structure (1)");
        exit(EXIT_FAILURE);
    }

    // Read data from keyboard and allocation of structure fields
    
    printf("Lastname : ");
    if(scanf("%255s", buffer) != 1) {
        fprintf(stderr, "Error reading lastname\n");
        exit(EXIT_FAILURE);
    }
    while(((c = getchar()) != '\n') && (c != EOF));    
    
    if((p->lastname = malloc(sizeof(char) * (strlen(buffer) + 1))) == NULL) {
        perror("Error allocating field lastname (1)");
        exit(EXIT_FAILURE);
    }
    strcpy(p->lastname, buffer);
    
    printf("Firstname: ");
    if(scanf("%255s", buffer) != 1) {
        fprintf(stderr, "Error reading firstname\n");
        exit(EXIT_FAILURE);
    }
    while(((c = getchar()) != '\n') && (c != EOF));
    
    if((p->firstname = (char*)malloc(sizeof(char) * (strlen(buffer) + 1))) == NULL) {
        perror("Error allocating field firstname (2)");
        exit(EXIT_FAILURE);
    }
    strcpy(p->firstname, buffer);
    
    printf("Age      : ");
    if(scanf("%d", &(p->age)) != 1) {
        fprintf(stderr, "Erreur lors de la saisie de l'âge\n");
        exit(EXIT_FAILURE);
    }
      
    // Save structure into file
    if((fd = open("toto.bin", O_WRONLY|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error creating file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    // Write lastname and size
    size = (strlen(p->lastname) + 1) * sizeof(char);
    if(write(fd, &size, sizeof(size_t)) == -1) {
        perror("Error saving lastname size");
        exit(EXIT_FAILURE);
    }
    if(write(fd, p->lastname, size) == -1) {
        perror("Error saving lastname");
        exit(EXIT_FAILURE);
    }
    printf("Lastname written.\n");
    
    // Write firstname and size
    size = (strlen(p->firstname) + 1) * sizeof(char);
    if(write(fd, &size, sizeof(size_t)) == -1) {
        perror("Error saving firstname size");
        exit(EXIT_FAILURE);
    }
    if(write(fd, p->firstname, size) == -1) {
        perror("Error saving firstname");
        exit(EXIT_FAILURE);
    }
    printf("Firstname written.\n");
    
    // Write age
    if(write(fd, &(p->age), sizeof(int)) == -1) {
        perror("Error saving age");
        exit(EXIT_FAILURE);
    }
    printf("Age written.\n");

    // Close file
    if(close(fd) == -1) {
        perror("Error closing file (1)");
        exit(EXIT_FAILURE);
    }
    printf("Structure written.\n");

    // Free memory
    free(p->lastname);
    free(p->firstname);
    free(p);
    printf("Memory freed.\n");
    
    // Structure allocation
    if((p = (person_t*)malloc(sizeof(person_t))) == NULL) {
        perror("Error allocating structure (2)");
        exit(EXIT_FAILURE);
    }

    // Open file
    if((fd = open("toto.bin", O_RDONLY, S_IRUSR|S_IWUSR)) == -1) {
        perror("Error opening file 'toto.bin'");
        exit(EXIT_FAILURE);
    }

    // Read lastname size and lastname
    if(read(fd, &size, sizeof(size_t)) == -1) {
        perror("Error reading lastname size");
        exit(EXIT_FAILURE);
    }    
    if((p->lastname = malloc(size)) == NULL) {
        perror("Error allocating lastname field (2)");
        exit(EXIT_FAILURE);
    }
    if(read(fd, p->lastname, size) == -1) {
        perror("Error reading lastname");
        exit(EXIT_FAILURE);
    }
    printf("Lastname readed.\n");
    
    // Read firstname size and firstname
    if(read(fd, &size, sizeof(size_t)) == -1) {
        perror("Error reading firstname size");
        exit(EXIT_FAILURE);
    }    
    if((p->firstname = malloc(size)) == NULL) {
        perror("Error allocating firstname field (2) ");
        exit(EXIT_FAILURE);
    }
    if(read(fd, p->firstname, size) == -1) {
        perror("Error reading firstname");
        exit(EXIT_FAILURE);
    }
    printf("Firstname readed.\n");
    
    // Read age
    if(read(fd, &(p->age), sizeof(int)) == -1) {
        perror("Error reading age");
        exit(EXIT_FAILURE);
    }
    printf("Age readed.\n");
    
    printf("%s %s (%d year(s) old)\n", p->firstname, p->lastname, p->age);
    
    // Free memory
    free(p->lastname);
    free(p->firstname);
    free(p);

    // Close file
    if(close(fd) == -1) {
        perror("Error closing file (2)");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}