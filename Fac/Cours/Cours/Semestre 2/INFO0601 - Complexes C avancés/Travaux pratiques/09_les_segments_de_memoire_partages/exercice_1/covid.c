#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ncurses.h>
#include <signal.h>
#include <time.h>
#include <sys/shm.h>

#include "include.h"

int stop = 0;

/**
 * Handler for the SIGINT signal.
 * @param signum the signal number (SIGINT)
 */
void handler(int signum) {
    printf("End signal received.\n");
    stop = 1;
}

/**
 * Returns a random integer in intervalle [a, b].
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Main function.
 * @param argc the number of arguments
 * @param argv arguments
 * @return the return code
 */
int main(int argc, char *argv[]) {
    unsigned char *map;
    int i, j, index, newx, newy, direction;
    struct sigaction action;

    // Initialize the pseudo-random number generator
    srand(time(NULL) + getpid());

    // #TODO# #6 delete this instruction
    map = malloc(sizeof(unsigned char) * WIDTH * HEIGHT);
    
    // Get the shared memory segment and attach it
    // #TODO# #7 get the shared memory segement and attach it

    // Position a handler
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning the handler");
        exit(EXIT_FAILURE);    
    }
    
    // Main loop
    while(stop == 0) {
        index = 0;
        for(j = 0; j < HEIGHT; j++) {
            for(i = 0; i < WIDTH; i++) {
                if(map[index] == 'C') {
                    // Move a virus
                    map[index] = ' ';

                    // Select a new position
                    newx = i;
                    newy = j;
                    direction = random_integer(0, 3);
                    switch(direction) {
                        case 0:
                            if(newx < WIDTH - 1)
                                newx++;
                            break;
                        case 1:
                            if(newy < HEIGHT - 1)
                                newy++;
                            break;
                        case 2:
                            if(newx > 0)
                                newx--;
                            break;
                        case 3:
                            if(newy > 0)
                                newy--;
                            break;
                    }

                    if(map[newy * WIDTH + newx] != ' ') {
                        // Virus doesn't move
                        map[index] = 'M';
                    }
                    else {
                        // Virus moves to new position
                        map[newy * WIDTH + newx] = 'M';
                    }
                }
                else if((map[index] == ' ') &&
                        ((i == 0) || (i == WIDTH - 1) || (j == 0) || (j == HEIGHT - 1))) {
                    if(random_integer(0, MAX) < CREATE) {
                        // Create a new virus
                        map[index] = 'C';
                    }
                }
                index++;
            }
        }
        
        // Replacement of M by C
        i = 0;
        for(j = 0; j < HEIGHT * WIDTH; j++) {
            if(map[j] != ' ') {
                map[j] = 'C';
                i++;
            }
        }
        printf("%d virus(es)\n", i);
        
        // Pause
        usleep(SPEED);
    }
    
    printf("%s: stoped\n", argv[0]);
    
    // Detach the segment
    // #TODO# #8 detach the segment
 
    // #TODO# #9 delete this instruction
    free(map);
 
    return EXIT_SUCCESS;
}