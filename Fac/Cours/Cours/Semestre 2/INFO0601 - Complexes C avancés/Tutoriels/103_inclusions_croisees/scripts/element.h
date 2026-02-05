#ifndef _ELEMENT_
#define _ELEMENT_

// Types of element
typedef enum { TYPE_UNDEF = -1, TYPE_INT = 0, TYPE_ARRAY = 1, TYPE_OBJECT = 2 } type_t;

#define MAX_STR              20

typedef struct array_t array_t;
typedef struct object_t object_t;

// The value of an element
typedef union {
    array_t *array;
    object_t *object;
    int integer;
} value_t;

// The structure of an element
typedef struct {
    type_t type;
    value_t value;
} element_t;

/**
 * Create a new element.
 * @param type the type (TYPE_INT, TYPE_ARRAY, TYPE_OBJECT)
 * @param value the value
 * @return the element
 */
element_t *element_create(int type, value_t value);

/**
 * Display an element on screen.
 * @param element the element
 */
void element_display(element_t *element);

/**
 * Delete an element.
 * @param element the element
 */
void element_delete(element_t **element);

#endif