/**
* A ping pong game based on the use of real-time signals.
 * The server and the client exchange values ​​using real-time signals. Whoever
 * receives a value that is 2 higher or lower than that of his opponent loses
 * the game.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>

#include "utils.h"

int main(int argc, char *argv[]) {
    sigset_t set;
    siginfo_t info;
    int stop = 0, player = 0;
    union sigval value;
    pid_t server_pid;

    srand(time(NULL) + getpid()); 
    
    if(argc != 2) {
        fprintf(stderr, "Use: %s PID where PID is the server PID.\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    server_pid = atoi(argv[1]);
    
    // Block the SIGRTMIN+1 signal
    sigemptyset(&set);
    sigaddset(&set, SIGRTMIN + 1);
    if(sigprocmask(SIG_BLOCK, &set, NULL) == -1) {
        perror("Error blocking signal");
        exit(EXIT_FAILURE);
    }
    
    // Main loop
    while(stop == 0) {
        if(player == 0) {
            // Send SIGRTMIN+1 to the server
            sleep(1);
            value.sival_int = _random(1, 5);
            printf("Client: send value %d\n", value.sival_int);
            if(sigqueue(server_pid, SIGRTMIN + 1, value) == -1) {
                perror("Client: error sending signal");
                exit(EXIT_FAILURE);
            }
            player = 1 - player;
        }
        else {
            // Wait for the SIGRTMIN+1 signal of the server
            sigemptyset(&set);
            sigaddset(&set, SIGRTMIN + 1);
            printf("Client: waiting for server signal.\n");
            if(sigwaitinfo(&set, &info) == -1) {
                perror("Server: error waiting for server signal");
                exit(EXIT_FAILURE);
            }
            printf("Client: client = %d and server = %d.\n", value.sival_int, info.si_value.sival_int);
            if(info.si_value.sival_int == 0) {
                printf("Client: I won!!!\n");
                stop = 1;
            } else if((value.sival_int < info.si_value.sival_int - 1) ||
                    (value.sival_int > info.si_value.sival_int + 1)) {            
                printf("Client: I lost!!!\n");
                value.sival_int = 0;
                if(sigqueue(server_pid, SIGRTMIN + 1, value) == -1) {
                    perror("Client: error sending end signal to the server");
                    exit(EXIT_FAILURE);
                }
                stop = 1;
            } else {
                printf("Client: I caught the ball.\n");
                player = 1 - player;
            }
        }
    }    
        
    return EXIT_SUCCESS;
}