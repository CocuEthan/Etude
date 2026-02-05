/**
 * Size of structures with alignment.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>

/* Structure 1 */
typedef struct {
    unsigned int a;
    short b;
    float c;
    double d;
} structure1_t;

/* Structure 1 - manual alignment */
typedef struct {
    unsigned int a;
    short b;
    char _pad1[2];
    float c;
    char _pad2[4];
    double d;
} structure1b_t;

/* Structure 2 */
typedef struct {
  char a;
  double b;
  char c[2];
  int d[2];
} structure2_t;

/* Structure 2 - manual alignment */
typedef struct {
  char a;
  char c[2];
  char _pad1[5];
  double b;
  int d[2];
} structure2b_t;

int main() {
    structure1_t s1;
    structure2_t s2;
    structure1b_t s3;
    structure2b_t s4;

    printf("Size: %ld\n", sizeof(s1));
    printf("Size: %ld\n", sizeof(s2));

    printf("Size: %ld\n", sizeof(s3));
    printf("Size: %ld\n", sizeof(s4));
    
    return EXIT_SUCCESS;
}