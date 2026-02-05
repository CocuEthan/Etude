/**
 * Structures size.
 */
#include <stdlib.h>
#include <stdio.h>

typedef struct {
  float a;
  char b;
  char c;
  float d;
} structure1_t;

typedef struct {
  char a;
  char b;
  double c;
  char d;
} structure2_t;

typedef struct {
  float a;
  long b;
  long long int c;
  int d;
} structure3_t;

int main() {
    structure1_t s1;
    structure2_t s2;
    structure3_t s3;
    
    printf("Structure #1: size = %ld\n", sizeof(s1));
    printf("Structure #2: size = %ld\n", sizeof(s2));
    printf("Structure #3: size = %ld\n", sizeof(s3));
    
    return EXIT_SUCCESS;
}