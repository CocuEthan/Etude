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

int main(int argc, char *argv[]) {
    pid_t pid;
    
    // Check arguments
    if(argc != 2) {
        fprintf(stderr, "Use: %s PID where PID is the PID of the 'server'\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    pid = atoi(argv[1]);
    
    // Send the SIGUSR1 signal
    if(kill(pid, SIGUSR1) == -1) {
        perror("Error sending the SIGUSR1 signal");
        exit(EXIT_FAILURE);
    }
    printf("Signal SIGUSR1 sent.\n");
    sleep(1);
    
    // Send the SIGUSR2 signal
    if(kill(pid, SIGUSR2) == -1) {
        perror("Error sending the SIGUSR2 signal");
        exit(EXIT_FAILURE);
    }
    printf("Signal SIGUSR2 sent.\n");
  
    return EXIT_SUCCESS;
}