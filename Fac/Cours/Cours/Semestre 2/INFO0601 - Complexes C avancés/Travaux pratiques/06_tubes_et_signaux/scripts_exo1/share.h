#ifndef _SHARED_
#define _SHARED_

#define MAX_LENGTH  15
#define MAX_SIZE    10

#define REQUEST_GET  0
#define REQUEST_SET  1
#define REQUEST_SIZE 2

#include <sys/types.h>

typedef struct {
    pid_t pid;
    int type;
    int cell;
    int value;
} share_request_t;

typedef struct {
    char filename[256];
    int fd;
    int size;
} share_t;

/**
 * Get a shared array.
 * @param variable_name the name of the array
 * @return the shared array
 */
share_t share_init(char *variable_name);

/**
 * Clean a shared array.
 * @param array the shared array
 */
void share_clean(share_t array);

/**
 * Get the size of the array.
 * @param array the shared array
 * @return the cell value
 */
int share_size(share_t array);

/**
 * Get a cell value.
 * @param array the shared array
 * @param cell the number of the cell
 * @return the cell value
 */
int share_get(share_t array, int cell);

/**
 * Get a cell value.
 * @param array the shared array
 * @param cell the number of the cell
 * @return the cell value
 */
void share_set(share_t array, int cell, int value);

#endif