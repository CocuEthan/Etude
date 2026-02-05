#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "element.h"
#include "object.h"

/**
 * Create a new object with nb members.
 * @param nb the member number
 * @return the object
 */
object_t *object_create(int nb) {
    object_t *result;
    int i;
    
    if((result = malloc(sizeof(object_t))) == NULL) {
        fprintf(stderr, "Error allocating object\n");
        exit(EXIT_FAILURE);
    }
    
    result->nb = nb;
    
    if((result->members = malloc(sizeof(member_t) * nb)) == NULL) {
        fprintf(stderr, "Error allocating object members\n");
        exit(EXIT_FAILURE);
    }
    
    memset(result->members, 0, sizeof(member_t) * nb);
    for(i = 0; i < nb; i++)
        result->members[i].value->type = TYPE_UNDEF;
    
    return result;
}

/**
 * Display an object on screen.
 * @param object the object
 */
void object_display(object_t *object) {
    int i;
    
    printf("{ ");
    
    for(i = 0; i < object->nb; i++) {
        printf("\"%s\" : ", object->members[i].name);
        element_display(object->members[i].value);
        if(i < object->nb -1)
            printf(", ");
    }
    
    printf(" }");
}

/**
 * Delete an object.
 * @param object the object
 */
void object_delete(object_t **object) {
    int i;
    
    for(i = 0; i < (*object)->nb; i++) {
        element_delete(&(*object)->members[i].value);
    }
    free(*object);
    *object = NULL;
}