/**
 * Compute structures size and display fields of the structure.
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef struct {
  int *a;
  char b[2];
  char c[3];
  long double d;
} structure1_t;

typedef struct {
  int a;
  structure1_t b[2];
  char c[12];
  int d;
} structure2_t;

typedef union {
  char a;
  double b;
  char *c;
  short d;
} structure3_t;

/**
 * Display fields structure.
 * @param ptr a pointer to the structure
 * @param size the size of the structure
 */
void display(char *ptr, int size) {
    int i;
    
    for(i = 0; i < size; i++) {
        if((i + 1) % 4 == 0)
            printf("%d",(i+1) / 10);
        else
            printf(" ");
    }
    printf("\n");
    for(i = 0; i < size; i++) {
        if((i + 1) % 4 == 0)
            printf("%d",(i+1) % 10);
        else
            printf(" ");
    }
    printf("\n");
    for(i = 0; i < size; i++) {
        printf("%c", ptr[i]);
    }
    printf("\n");
}

int main() {
    structure1_t s1;
    structure2_t s2;
    structure3_t s3;
    
    printf("Structure #1: size = %ld\n", sizeof(s1));
    
    memset(&s1, '?', sizeof(s1));
    memset(&(s1.a), 'a', sizeof(s1.a));
    memset(&(s1.b), 'b', sizeof(s1.b));
    memset(&(s1.c), 'c', sizeof(s1.c));
    memset(&(s1.d), 'd', sizeof(s1.d));
    
    display((char*)&s1, sizeof(s1));
    printf("\n");
    
    printf("Structure #2: size = %ld\n", sizeof(s2));
    
    memset(&s2, '?', sizeof(s2));
    memset(&(s2.a), 'a', sizeof(s2.a));
    memset(&(s2.b), 'b', sizeof(s2.b));
    memset(&(s2.c), 'c', sizeof(s2.c));
    memset(&(s2.d), 'd', sizeof(s2.d));
    
    display((char*)&s2, sizeof(s2));
    printf("\n");
    
    printf("Structure #3: size = %ld\n", sizeof(s3));
    
    memset(&s3, '?', sizeof(s3));
    memset(&(s3.a), 'a', sizeof(s3.a));
    memset(&(s3.b), 'b', sizeof(s3.b));
    memset(&(s3.c), 'c', sizeof(s3.c));
    memset(&(s3.d), 'd', sizeof(s3.d));
    
    display((char*)&s3, sizeof(s3));
    printf("\n");
    
    return EXIT_SUCCESS;
}