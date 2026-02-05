/**
 * Passing a structure as a parameter. This structure has dynamic fields.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
  char *lastname;
  char *firstname;
  int age;
} person_t;

void method(person_t p) {
  printf("(1): %s %s (%d year(s) old)\n", p.lastname, p.firstname, p.age);
  p.lastname[2] = '\0';
  p.age = 30;
  printf("(2): %s %s (%d an(s) old)\n", p.lastname, p.firstname, p.age);
}

int main() {
  person_t p1;
  
  if((p1.lastname = (char*)malloc(sizeof(char) * 5)) == NULL) {
      perror("Error allocating (1)");
      exit(EXIT_FAILURE);
  }
  
  if((p1.firstname = (char*)malloc(sizeof(char) * 5)) == NULL) {
      perror("Error allocating (2)");
      exit(EXIT_FAILURE);      
  }
  
  strcpy(p1.lastname, "Toto");
  strcpy(p1.firstname, "Tata");
  p1.age = 40;
 
  method(p1);
  printf("(3): %s %s (%d year(s) old)\n", p1.lastname, p1.firstname, p1.age);
  
  free(p1.lastname);
  free(p1.firstname);
  
  return EXIT_SUCCESS;
}