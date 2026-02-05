/**
 * The server sets a handler for the SIGUSR1 and SIGUSR2 signals. Then, it
 * waits for the client to send these signals.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

int cpt = 0; /* Global counter */

/**
 * Handler for SIGUSR1 and SIGUSR2 signals.
 * @param signum the received signal number
 */
void handler(int signum) {
    if(signum == SIGUSR1) {
        printf("Signal 1 received\n");
        cpt = cpt | 1;
    }
    if(signum == SIGUSR2) {
        printf("Signal 2 received\n");
        cpt = cpt | 2;
    }
}

int main() {
    struct sigaction action;

    // Specify the handler for the SIGUSR1 and SIGUSR2 signals
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGUSR1, &action, NULL) == -1) {
        perror("Error positioning handler for SIGUSR1");
        exit(EXIT_FAILURE);
    }    
    if(sigaction(SIGUSR2, &action, NULL) == -1) {
        perror("Error positioning handler for SIGUSR2");
        exit(EXIT_FAILURE);
    }

    printf("Ready to receive signals, PID=%d\n", getpid());
    while(cpt != 3) {
        sleep(1);
    }

    return EXIT_SUCCESS;
}