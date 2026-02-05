/**
 * This program creates a child process and sends it the real-time signal
 * SIGRTMIN+1.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>

/**
 * Handler for SIGRTMIN + 1 signal.
 * @param num_sig the received signal number
 * @param info a pointer to signal information
 * @param nothing the signal context information
 */
void handler(int num_sig, siginfo_t *info, void *nothing) {
    printf("Child: value received = %d\n", info->si_value.sival_int);
}

/**
 * The child main function.
 */
void child() {
    struct sigaction action;

    // Specify the handler for the SIGRTMIN + 1 signal
    action.sa_sigaction = handler;
    sigemptyset(&action.sa_mask);
    action.sa_flags = SA_SIGINFO;
    if(sigaction(SIGRTMIN + 1, &action, NULL) == -1) {
        perror("Child: error positioning handler");
        exit(EXIT_FAILURE);
    }

    printf("Child: I wait for the signal\n");
    pause();
    printf("Child: done\n");

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

    // Sleep during 2s
    printf("Father: I wait for 2s\n");
    sleep(2);

    // Send the signal with the value
    value.sival_int = 1234;
    if(sigqueue(pid, SIGRTMIN + 1, value) == -1) {
        perror("Father: error sending signal");
        exit(EXIT_FAILURE);
    }
    printf("Father: signal sent to child\n");

    // Wait for the child end
    if(wait(NULL) == -1) {
        perror("Error waiting for child end");
        exit(EXIT_FAILURE);
    }
    printf("Father: the child is stopped\n");

    return EXIT_SUCCESS;
}