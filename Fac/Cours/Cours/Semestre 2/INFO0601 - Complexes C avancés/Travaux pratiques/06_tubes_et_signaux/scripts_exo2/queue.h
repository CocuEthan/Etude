#ifndef _QUEUE_
#define _QUEUE_

#define QUEUE_SIZE  10

#include <sys/types.h>

// Structure for the PID queue
typedef struct {
    pid_t queue[QUEUE_SIZE];
    int head;
    int end;
} queue_t;

/**
 * Initialize a queue.
 * @return the queue
 */
queue_t queue_init();

/**
 * Create a queue.
 * @return the queue
 */
int queue_isfull(queue_t *queue);

/**
 * Create a queue.
 * @return the queue
 */
int queue_isempty(queue_t *queue);

/**
 * Create a queue.
 * @return the queue
 */
int queue_get(queue_t *queue);

/**
 * Add a value.
 * @return the queue
 */
int queue_add(queue_t *queue, int value);

#endif