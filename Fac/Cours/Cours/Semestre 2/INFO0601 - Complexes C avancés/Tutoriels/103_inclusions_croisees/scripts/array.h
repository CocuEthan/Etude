#ifndef _ARRAY_
#define _ARRAY_

// The array structure
typedef struct array_t {
    int length;
    element_t **cells;
} array_t;

/**
 * Create a new array with a specified length.
 * @param length the length
 * @return the array
 */
array_t *array_create(int length);

/**
 * Display an array on screen.
 * @param array the array
 */
void array_display(array_t *array);

/**
 * Delete an array.
 * @param array the array
 */
void array_delete(array_t **array);

#endif