#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "element.h"
#include "array.h"

/**
 * Create a new array with a specified length.
 * @param length the length
 * @return the array
 */
array_t *array_create(int length) {
    array_t *result;
    
    if((result = malloc(sizeof(array_t))) == NULL) {
        fprintf(stderr, "Error allocating array\n");
        exit(EXIT_FAILURE);
    }
    
    result->length = length;
    
    if((result->cells = malloc(sizeof(element_t*) * length)) == NULL) {
        fprintf(stderr, "Error allocating array elements\n");
        exit(EXIT_FAILURE);
    }
    
    memset(result->cells, 0, sizeof(element_t*) * length);
    
    return result;    
}

/**
 * Display an array on screen.
 * @param array the array
 */
void array_display(array_t *array) {
    int i;
    
    printf("[ ");
    
    for(i = 0; i < array->length; i++) {
        element_display(array->cells[i]);
        if(i < array->length - 1)
            printf(", ");
    }
    
    printf(" ]");
}

/**
 * Delete an array.
 * @param array the array
 */
void array_delete(array_t **array) {
    int i;
    
    for(i = 0; i < (*array)->length; i++) {
        element_delete(&(*array)->cells[i]);
    }
    free(*array);
    *array = NULL;
}