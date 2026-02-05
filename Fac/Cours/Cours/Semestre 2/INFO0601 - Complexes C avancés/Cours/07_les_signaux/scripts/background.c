/**
 * Program to test CRTL+Z in terminal and `fg` or `bg` commands.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

int stop = 1;

/** 
 * Handler for SIGINT signal.
 * @param signum the received signal number
 */
void handler(int signum) {
    printf("I received a signal; I stop...\n");
    stop = 0;
}

int main() {
    struct sigaction action;
    
    // Specify the handler for the SIGINT signal
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGINT, &action, NULL) == -1) {
        perror("Error positioning handler");
        exit(EXIT_FAILURE);
    }
    
    // Help
    printf("After starting this program, open a second terminal and run `top`.\n");
    printf("Type CRTL+Z to stop this program and check the modified state with top.\n");
    printf("Now, type CRTL+C in first terminal: there is no effect for this program.\n");
    printf("Type `bg` to unlock the process or `fg` to move it in foreground.\n");
    
    // Main loop: stop when a SIGINT signal is received
    while(stop) {
        sleep(1);
    }
    
    return EXIT_SUCCESS;
}