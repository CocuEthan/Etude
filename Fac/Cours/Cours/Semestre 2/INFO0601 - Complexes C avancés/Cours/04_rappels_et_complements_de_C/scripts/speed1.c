/**
 * Comparison of speed according to the type of parameter passing
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

typedef struct {
  char lastname[256];
  char firstname[256];
  int age;
} person_t;

void method1(person_t p) {

}

void method2(person_t *p) {

}

int main() {
    int i, j;
    person_t p1 = { "Toto", "Tata", 40 };
    time_t t1, t2;

    printf("Passing structure without pointer\n");
    time(&t1);
    for(i = 0; i < 100000; i++)
        for(j = 0; j < 50000; j++)
            method1(p1);
    time(&t2);
    printf("Time 1: %lds\n", t2-t1);

    printf("Passing structure with pointer\n");
    time(&t1);
    for(i = 0; i < 100000; i++)
        for(j = 0; j < 50000; j++)
            method2(&p1);
    time(&t2);
    printf("Time 2: %lds\n", t2-t1);
  
    return EXIT_SUCCESS;
}