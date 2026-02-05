#ifndef _DIJKSTRA_
#define _DIJKSTRA_

#define MAX_SEMS 10

typedef struct {
    pid_t server_pid;
} sem_t;

/**
 * Initialize a semaphore set.
 * @param pid the pid of the server
 * @return the semaphore set configuration
 */
sem_t sem_init(pid_t pid);

/**
 * Clean the semaphore set.
 * @param sem the semaphore set
 */
void sem_clean(sem_t sem);

/**
 * P semaphore operation
 * @param sem the semaphore set configuration
 * @param num the semaphore number
 * @return 1 on success
 */
int sem_P(sem_t sem, int num);

/**
 * V semaphore operation
 * @param sem the semaphore set configuration
 * @param num the semaphore number
 * @return 1 on success 
 */
int sem_V(sem_t sem, int num);

#endif