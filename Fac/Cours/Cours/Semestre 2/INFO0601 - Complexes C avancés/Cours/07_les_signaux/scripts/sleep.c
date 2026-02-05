/**
 * The program sleeps using `sleep` and `nanosleep`.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main() {
    struct timespec time = { 1, 500000000 };

    printf("I sleep during 1s...\n");
    sleep(1);

    printf("I sleep during 1.5s...\n");
    if(nanosleep(&time, NULL) == -1) {
        perror("Error initializing pause");
        exit(EXIT_FAILURE);
    }
    
    return EXIT_SUCCESS;
}