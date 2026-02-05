/**
 * Passing a structure as a parameter. This structure has only static fields.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>

typedef struct {
  char lastname[256];
  char firstname[256];
  int age;
} person_t;

void method(person_t p) {
  printf("(1): %s %s (%d year(s) old)\n", p.lastname, p.firstname, p.age);
  p.lastname[2] = '\0';
  p.age = 30;
  printf("(2): %s %s (%d year(s) old)\n", p.lastname, p.firstname, p.age);
}

int main() {
  person_t p1 = { "Toto", "Tata", 40 };
 
  method(p1);
  printf("(3): %s %s (%d year(s) old)\n", p1.lastname, p1.firstname, p1.age);
  
  return EXIT_SUCCESS;
}