/**
 * A ping pong game based on the use of real-time signals.
 * The server and the client exchange values ​​using real-time signals. Whoever
 * receives a value that is 2 higher or lower than that of his opponent loses
 * the game.
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>

#include "utils.h"

int main() {
    pid_t pid, client_pid;
    sigset_t set;
    int stop = 0, player = 1;
    siginfo_t info;
    union sigval value;
 
    srand(time(NULL) + getpid()); 
 
    pid = getpid();
    printf("Server: my PID is %d.\n", pid);
    
    // Block the SIGRTMIN+1 signal
    sigemptyset(&set);
    sigaddset(&set, SIGRTMIN + 1);
    if(sigprocmask(SIG_BLOCK, &set, NULL) == -1) {
        perror("Server: error blocking signal");
        exit(EXIT_FAILURE);
    }
    
    // Main loop
    while(stop == 0) {
        if(player == 0) {
            // Send SIGRTMIN+1 to the client
            sleep(1);
            printf("Server: send value %d\n", value.sival_int);
            sigqueue(client_pid, SIGRTMIN+1, value);
            player = 1 - player;
        }
        else {
            // Wait for SIGRTMIN+1 from the client
            sigemptyset(&set);
            sigaddset(&set, SIGRTMIN + 1);
            printf("Server: waiting for client signal.\n");
            if(sigwaitinfo(&set, &info) == -1) {
                perror("Server: error waiting for client signal");
                exit(EXIT_FAILURE);
            }
            
            client_pid = info.si_pid;
            value.sival_int = _random(1, 5);
            printf("Server: client = %d and server = %d.\n", info.si_value.sival_int, value.sival_int);
            
            if(info.si_value.sival_int == 0) {
                printf("Server: I won!!!\n");
                stop = 1;
            } else if((value.sival_int < info.si_value.sival_int - 1) ||
                      (value.sival_int > info.si_value.sival_int + 1)) {            
                printf("Server: I lost!!!\n");
                
                // Send the end signal to the client
                value.sival_int = 0;
                if(sigqueue(client_pid, SIGRTMIN+1, value) == -1) {
                    perror("Server: error sending end signal to the client");
                    exit(EXIT_FAILURE);
                }
                stop = 1;
            } else {
                printf("Server: I caught the ball.\n");
                player = 1 - player;
            }
        }
    }    
    
    return EXIT_SUCCESS;
}    