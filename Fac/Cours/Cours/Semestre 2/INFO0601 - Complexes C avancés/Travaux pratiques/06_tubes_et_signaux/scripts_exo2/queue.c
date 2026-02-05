#include "queue.h"

/**
 * Initialize a queue.
 * @return the queue
 */
queue_t queue_init() {
    queue_t result;
    
    result.head = 0;
    result.end = 0;
    
    return result;
}    

/**
 * Check if the queue is full.
 * @param queue the queue
 * @return 'true' if the queue is full
 */
int queue_isfull(queue_t *queue) {
    return (queue->head + 1) % QUEUE_SIZE == queue->end;
}

/**
 * Check if the queue is empty.
 * @param queue the queue
 * @return 'true' if the queue is empty
 */
int queue_isempty(queue_t *queue) {
    return queue->head == queue->end;
}

/**
 * Get the next value of the queue.
 * @return the next value (or -1 if the queue is empty)
 */
int queue_get(queue_t *queue) {
    int result = -1;
    
    if(!queue_isempty(queue)) {
        result = queue->queue[queue->end];
        queue->end = (queue->end + 1) % QUEUE_SIZE;
    }
    
    return result;    
}

/**
 * Add a value in the queue.
 * @param queue the queue
 * @param value the value
 * @return 'true' if the value is added
 */
int queue_add(queue_t *queue, int value) {
    int result = 0; 
    if(!queue_isfull(queue)) {
        queue->queue[queue->head] = value;
        queue->head = (queue->head + 1) % QUEUE_SIZE;
        result = 1;
    }
    return result;
}