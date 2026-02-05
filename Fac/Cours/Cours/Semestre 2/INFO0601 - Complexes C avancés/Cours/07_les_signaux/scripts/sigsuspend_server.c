/**
 * The server waits to receive the SIGUSR1 signal sent by the client.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>

/**
 * Handler for signals.
 * @param signum the received signal number
 */
void handler(int signum) {
    /* Nothing to do here */
}

int main() {
    sigset_t sigs_new, sigs_wait;
    struct sigaction action;

    // Specify the handler for the SIGUSR1 signal
    sigemptyset(&action.sa_mask);
    action.sa_flags = 0;
    action.sa_handler = handler;
    if(sigaction(SIGUSR1, &action, NULL) == -1) {
        perror("Error positioning handler for the SIGUSR1 signal");
        exit(EXIT_FAILURE);
    }
    
    // Block all signals
    sigfillset(&sigs_new);
    if(sigprocmask(SIG_BLOCK, &sigs_new, NULL) == -1) {
        perror("Erreur lors du blocage des signaux ");
        exit(EXIT_FAILURE);
    }

    // Prepare the set with excepted signals
    sigfillset(&sigs_wait);
    sigdelset(&sigs_wait, SIGUSR1);

    // Wait for SIGUSR1 signal
    printf("Ready to receive SIGUSR1, PID=%d\n", getpid());
    if(sigsuspend(&sigs_wait) == -1) {
        if(errno != EINTR) {
            perror("Error waiting for signal");
            exit(EXIT_FAILURE);
        }
    }
    printf("It's good, I received SIGUSR1.\n");
  
    return EXIT_SUCCESS;
}