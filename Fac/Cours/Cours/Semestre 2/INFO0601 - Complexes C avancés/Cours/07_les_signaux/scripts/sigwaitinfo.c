/**
 * Programme illustrant le fonctionnement de sigwaitinfo. Le programme crée un
 * processus fils. Ce dernier attend l'envoi du signal SIGRTMIN + 1 qui est
 * envoyé par le processus père.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>

/** 
 * The child main function.
 */
void child() {
    sigset_t set;
    siginfo_t info;

    // Block all signals
    sigfillset(&set); 
    if(sigprocmask(SIG_BLOCK, &set, NULL) == -1) {
        perror("Child: error blocking signals");
        exit(EXIT_FAILURE);
    }

    // Wait for the SIGRTMIN+1 signal
    sigemptyset(&set);
    sigaddset(&set, SIGRTMIN + 1);
    printf("Child: I wait for the SIGRTMIN+1 signal\n");
    if(sigwaitinfo(&set, &info) == -1) {
        perror("Error waiting signal");
        exit(EXIT_FAILURE);
    }
    printf("Child: I received the signal with the value %d\n", info.si_value.sival_int);

    exit(EXIT_SUCCESS);
}

int main() {
    pid_t pid;
    union sigval value;

    // Create a child process
    if((pid = fork()) == -1) {
        perror("Father: error creating child");
        exit(EXIT_FAILURE);
    }
    if(pid == 0)
        child();

    printf("Father: I wait for 2s\n");
    sleep(2);

    // Send the signal
    value.sival_int = 1234;
    if(sigqueue(pid, SIGRTMIN + 1, value) == -1) {
        perror("Error sending signal");
        exit(EXIT_FAILURE);
    }
    printf("Father: signal sent to the child\n");

    // Wait for the child end
    if(wait(NULL) == -1) {
        perror("Error waiting child end");
        exit(EXIT_FAILURE);
    }
    printf("Father: the child is stopped\n");

    return EXIT_SUCCESS;
}