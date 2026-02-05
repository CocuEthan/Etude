#include <stdio.h>
#include <stdlib.h>

#include "element.h"
#include "array.h"
#include "object.h"

int main() {
    element_t *element;
    array_t *array;
    object_t *object, *object2;
    int i;
    value_t value;
    
    printf("Simple element example:\n");
    value.integer = 1940;
    element = element_create(TYPE_INT, value);
    element_display(element);
    printf("\n");
    element_delete(&element);
    
    printf("Array example:\n");
    array = array_create(3);
    for(i = 0; i < 3; i++) {
        value.integer = i;
        array->cells[i] = element_create(TYPE_INT, value);
    }
    array_display(array);
    printf("\n");
    array_delete(&array);
    
    printf("Object example:\n");
    object = object_create(3);
    for(i = 0; i < 3; i++) {
        sprintf(object->members[i].name, "%i", i);
        value.integer = i;
        object->members[i].value = element_create(TYPE_INT, value);
    }
    object_display(object);
    printf("\n");
    object_delete(&object);
    
    printf("Mixed object example:\n");
    object2 = object_create(3);
    
    sprintf(object2->members[0].name, "integer");
    value.integer = 1940;
    object2->members[0].value = element_create(TYPE_INT, value);
    
    array = array_create(3);
    for(i = 0; i < 3; i++) {
        value.integer = i;
        array->cells[i] = element_create(TYPE_INT, value);
    }
    sprintf(object2->members[1].name, "array");
    value.array = array;
    object2->members[1].value = element_create(TYPE_ARRAY, value);
    
    object = object_create(3);
    for(i = 0; i < 3; i++) {
        sprintf(object->members[i].name, "%i", i);
        value.integer = i;
        object->members[i].value = element_create(TYPE_INT, value);
    }
    sprintf(object2->members[2].name, "object");
    value.object = object;
    object2->members[2].value = element_create(TYPE_OBJECT, value);
    
    object_display(object2);
    printf("\n");
    object_delete(&object2);
    
    return EXIT_SUCCESS;
}