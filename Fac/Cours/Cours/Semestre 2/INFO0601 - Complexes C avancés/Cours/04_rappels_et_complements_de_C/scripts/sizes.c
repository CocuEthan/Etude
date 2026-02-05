/**
 * Size of variables (`int`, `double` and static array)
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>

int main() {
    int i;
    double a;
    int array[10];
    
    int *j = malloc(sizeof(int));
    int *k = NULL;
    int *array2 = malloc(sizeof(int) * 10);
    
    printf("Size = %ld, %ld\n", sizeof(i), sizeof(int));
    printf("Size = %ld, %ld\n", sizeof(a), sizeof(double));
    printf("Size = %ld, %ld\n", sizeof(array), sizeof(int[10]));
    printf("Size = %ld, %ld, %ld\n", sizeof(j), sizeof(int*), sizeof(*j));
    printf("Size = %ld, %ld, %ld\n", sizeof(k), sizeof(int*), sizeof(*k));
    printf("Size = %ld, %ld\n", sizeof(array2), sizeof(*array2));
    
    return EXIT_SUCCESS;
}