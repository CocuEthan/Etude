#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>

/**
 * Add a list of integers.
 * @param nb the list length
 * @param ... the list of integers
 * @return the sum of integers
 */
int add(int nb, ...) {
    va_list lstPar;
    int sum = 0, i;

    va_start(lstPar, nb);
    for(i = 0; i < nb; i++) {
        sum += va_arg(lstPar, int);
    }
    va_end(lstPar);
    
    return sum;
}

/**
 * Concatenate strings.
 * @param str the first string
 * @param ... a list of strings NULL terminated
 * @return a string
 */
char* concat(char *str, ...) {
    char *result, *ptr;
    va_list lstPar;
    size_t length = 0;
    
    // Determinates the length of the final string
    va_start(lstPar, str);
    ptr = va_arg(lstPar, char*);
    while(ptr != NULL) {
        length += strlen(ptr);
        ptr = va_arg(lstPar, char*);
    }
    va_end(lstPar);
    
    if((result = malloc(sizeof(char) * (length + 1))) == NULL) {
        fprintf(stderr, "Error allocating string\n");
        exit(EXIT_FAILURE);
    }
    
    // Concatenate the strings
    va_start(lstPar, str);
    ptr = va_arg(lstPar, char*);
    length = 0;
    while(ptr != NULL) {
        strcat(&result[length], ptr);
        length += strlen(ptr);
        ptr = va_arg(lstPar, char*);
    }
    va_end(lstPar);
    
    return result;
}

int main() {
    char *str;
    
    printf("Add: %d\n", add(5, 1, 2, 3, 4, 5));
    
    str = concat("Hello. ", "Here ", "is ", "an ", "example ", "of ", "a ", "string ", "concatenation.", NULL);
    printf("Final string: %s\n", str);
    free(str);
    
    return EXIT_SUCCESS;
}