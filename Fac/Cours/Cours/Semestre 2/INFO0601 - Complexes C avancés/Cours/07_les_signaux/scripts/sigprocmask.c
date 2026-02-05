/**
 * This programs shows how sigprocmask works. It has no effect here.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

int main() {
    sigset_t sigs_new, sigs_old;

    // Block all signals except SIGINT and SIGQUIT
    sigfillset(&sigs_new);
    sigdelset(&sigs_new, SIGINT);
    sigdelset(&sigs_new, SIGQUIT);
    if(sigprocmask(SIG_BLOCK, &sigs_new, &sigs_old) == -1) {
        perror("Error blocking signals (1)");
        exit(EXIT_FAILURE);
    }

    // Here all signals are blocked except SIGINT and SIGQUIT...
    // and of course... SIGKILL and SIGSTOP

    // Replace old mask
    if(sigprocmask(SIG_SETMASK, &sigs_old, NULL) == -1) {
        perror("Error positioning old mask");
        exit(EXIT_FAILURE);
    }
  
    // Block only SIGINT and SIGQUIT signals
    sigemptyset(&sigs_new);
    sigaddset(&sigs_new, SIGINT);
    sigaddset(&sigs_new, SIGQUIT);
    if(sigprocmask(SIG_BLOCK, &sigs_new, &sigs_old) == -1) {
        perror("Error blocking signals (2)");
        exit(EXIT_FAILURE);
    }

    // Here only SIGINT and SIGQUIT are blocked...
    // and of course... SIGKILL and SIGSTOP

    // Replace old mask
    if(sigprocmask(SIG_SETMASK, &sigs_old, NULL) == -1) {
        perror("Erreur lors du repositionnement ");
        exit(EXIT_FAILURE);
    }
  
    // The rest of the code
  
    return EXIT_SUCCESS;
}