/**
 * The server blocks the SIGUSR2 signal during 10s. Then, it checks if it
 * has received signals.
 * The client sends the SIGUSR1 and SIGUSR2 signals.
 * Only the SIGUSR2 signal will be marked as pending.
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
    sigset_t sigs_new, sigs_blocked;
    struct sigaction action;
    unsigned int time = 10;

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
    
    // Block all signals except SIGUSR1
    sigfillset(&sigs_new);
    sigdelset(&sigs_new, SIGUSR1);
    if(sigprocmask(SIG_BLOCK, &sigs_new, NULL) == -1) {
        perror("Erreur lors du blocage des signaux ");
        exit(EXIT_FAILURE);
    }

    // Wait for 10s
    printf("Ready to receive SIGUSR1 and SIGUSR2, my PID=%d\n", getpid());
    while(time != 0)
        time = sleep(time);
    printf("End of my sleep\n");
    
    // Retreive the pending signals
    if(sigpending(&sigs_blocked) == -1) {
        perror("Error retreiving blocked signals");
        exit(EXIT_FAILURE);
    }
    
    // Check if the SIGUSR1 or SIGUSR2 signals are pending
    if(sigismember(&sigs_blocked, SIGUSR1))
        printf("I received the SIGUSR1 signal during my sleep.\n");
    else
        printf("I didn't receive the SIGUSR1 signal during my sleep.\n");
    if(sigismember(&sigs_blocked, SIGUSR2))
        printf("I received the SIGUSR2 signal during my sleep.\n");
    else
        printf("I didn't receive the SIGUSR2 signal during my sleep.\n");
  
    return EXIT_SUCCESS;
}