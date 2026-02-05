/**
 * Illustration en allocation statique et dynamique.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

#define FIRST  10000
#define SECOND 50000

typedef struct {
  char lastname[256];
  char firstname[256];
  int age;
} person_t;

int main() {
    int i, j;
    time_t t1, t2;
    
    printf("Create %d static structures\n", FIRST*SECOND);
    time(&t1);
    for(i = 0; i < FIRST; i++)
        for(j = 0; j < SECOND; j++) {
            person_t p;
            strcpy(p.lastname, "Toto");
            strcpy(p.firstname, "Tata");
            p.age = 40;
        }
    time(&t2);
    printf("Time 1: %lds\n", t2-t1);
    
    printf("Create %d dynamic structures with free\n", FIRST*SECOND);
    time(&t1);
    for(i = 0; i < FIRST; i++)
        for(j = 0; j < SECOND; j++) {
            person_t *p = malloc(sizeof(person_t));
            strcpy(p->lastname, "Toto");
            strcpy(p->firstname, "Tata");
            p->age = 40;
            free(p);
        }
    time(&t2);
    printf("Time 2: %lds\n", t2-t1);
    
    printf("Create %d dynamic structures without free\n", FIRST*SECOND);
    time(&t1);
    for(i = 0; i < FIRST; i++)
        for(j = 0; j < SECOND; j++) {
            person_t *p = malloc(sizeof(person_t));
            strcpy(p->lastname, "Toto");
            strcpy(p->firstname, "Tata");
            p->age = 40;
        }
    time(&t2);
    printf("Time 3: %lds\n", t2-t1);
  
    return EXIT_SUCCESS;
}