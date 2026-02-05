/**
 * Size of a structure with static fields.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>

typedef struct {
  char lastname[256];
  char firstname[256];
  int age;
} person_t;

int main() {
    person_t p1;
    person_t *p2 = (person_t*)malloc(sizeof(person_t));
    person_t *p3;

    printf("Size: %ld, %ld\n", sizeof(p1), sizeof(person_t));
    printf("Size: %ld, %ld, %ld\n", sizeof(p2), sizeof(*p2), sizeof(person_t*));
    printf("Size: %ld, %ld\n", sizeof(p3), sizeof(*p3));

    return EXIT_SUCCESS;
}