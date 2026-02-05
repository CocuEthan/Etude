/**
 * This program creates an unnamed local socket with socketpair.
 * The child sends random integers to the father which displays them and
 * return.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <sys/socket.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <sys/wait.h>

/**
 * Return a random integer in the interval [a,b].
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Function of each child.
 * @param out the file descriptor of the socket
 */
void child(int sockfd) {
    int i, value;

    // Initialize the random number generator
    srand(time(NULL) + getpid());

    // Main loop
    for(i = 0; i < 3; i++) {
        sleep(random_integer(1, 3));

        if(write(sockfd, &i, sizeof(int)) == -1) {
            perror("Child: error writing");
            exit(EXIT_FAILURE);
        }
        printf("Child: sent %d\n", i);

        sleep(aleatoire(1, 3));

        if(read(sockfd, &value, sizeof(int)) == -1) {
            perror("Child: error reading");
            exit(EXIT_FAILURE);
        }
        printf("Child: received %d\n", value);
    }

    // Close socket
    if(close(sockfd) == -1) {
        perror("Child: error closing socket");
        exit(EXIT_FAILURE);
    }

    printf("Child stopped.\n");

    exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[]) {
    int fd[2];
    pid_t pid;
    int i, value;

    // Create socket
    if(socketpair(AF_LOCAL, SOCK_STREAM, 0, fd) == -1) {
        perror("Father: error creating socket");
        exit(EXIT_FAILURE);
    }

    // Create son
    if((pid = fork()) == -1) {
        perror("Father: error creating child");
        exit(EXIT_FAILURE);
    }
    if(pid == 0) {
        // Close socket of the the father
        if(close(fd[0]) == -1) {
            perror("Child: error closing socket");
            exit(EXIT_FAILURE);
        }

        // Child function
        child(fd[1]);
    }

    // Close socket
    if(close(fd[1]) == -1) {
        perror("Father: error closing socket (1)");
        exit(EXIT_FAILURE);
    }

    // Main loop
    for(i = 0; i < 3; i++) {
        sleep(random_integer(1, 3));

        if(read(fd[0], &value, sizeof(int)) == -1) {
            perror("Father: error reading");
            exit(EXIT_FAILURE);
        }
        printf("Father: received %d\n", value);

        sleep(aleatoire(1, 3));

        if(write(fd[0], &i, sizeof(int)) == -1) {
            perror("Father: error writing");
            exit(EXIT_FAILURE);
        }
        printf("Father: sent %d\n", i);
    }

    // Wait for child end
    if(wait(NULL) == -1) {
        perror("Father: error waiting child");
        exit(EXIT_FAILURE);
    }

    // Close socket
    if(close(fd[0]) == -1) {
        perror("Father: error closing socket (2)");
        exit(EXIT_FAILURE);
    }

    printf("Father stopped.\n");

    return EXIT_SUCCESS;
}