#include <stdio.h>
#include <stdlib.h>

#include "element.h"
#include "array.h"
#include "object.h"

/**
 * Create a new element.
 * @param type the type (TYPE_INT, TYPE_ARRAY, TYPE_OBJECT)
 * @param value the value
 * @return the element
 */
element_t *element_create(int type, value_t value) {
    element_t *result;
    
    if((result = malloc(sizeof(element_t))) == NULL) {
        fprintf(stderr, "Error allocating element\n");
        exit(EXIT_FAILURE);
    }
    result->type = type;
    result->value = value;
    
    return result;
}

/**
 * Display an element on screen.
 * @param element the element
 */
void element_display(element_t *element) {
    switch((*element).type) {
        case TYPE_INT:
            printf("%d", element->value.integer);
            break;
        case TYPE_ARRAY:
            array_display(element->value.array);
            break;
        case TYPE_OBJECT:
            object_display(element->value.object);
            break;
        default:
            break;
    }
}

/**
 * Delete an element.
 * @param element the element
 */
void element_delete(element_t **element) {
    switch((*element)->type) {
        case TYPE_INT:
            break;
        case TYPE_ARRAY:
            break;
        case TYPE_OBJECT:
            break;
        default:
            break;
    }
    free(*element);
    *element = NULL;
}
