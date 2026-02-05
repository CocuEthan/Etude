/**
 * The program sets a 3s alarm with `alarm` and waits to receive the
 * SIGALRM signal with `pause`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

/**
 * Handler for the SIGALRM signal.
 * @param signum the received signal number
 */
void handler(int signum) {
    printf("I received an alarm signal.\n");
}

int main() {
    struct sigaction action;
    
    // Specify the handler for the SIGALRM signal
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGALRM, &action, NULL) == -1) {
        perror("Error positioning the handler");
        exit(EXIT_FAILURE);
    }
    
    // Set the 3s alarm
    alarm(3);
    
    // Wait to receive a signal
    printf("I wait for the alarm signal.\n");
    pause();
    printf("OK, it's finish!\n");
    
    return EXIT_SUCCESS;
}