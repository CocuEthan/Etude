#ifndef _OBJECT_
#define _OBJECT_

// Object member
typedef struct {
    char name[MAX_STR];
    element_t *value;
} member_t;

// Object structure
typedef struct object_t {
    int nb;
    member_t *members;
} object_t;

/**
 * Create a new object with nb members.
 * @param nb the member number
 * @return the object
 */
object_t *object_create(int nb);

/**
 * Display an object on screen.
 * @param object the object
 */
void object_display(object_t *object);

/**
 * Delete an object.
 * @param object the object
 */
void object_delete(object_t **object);

#endif