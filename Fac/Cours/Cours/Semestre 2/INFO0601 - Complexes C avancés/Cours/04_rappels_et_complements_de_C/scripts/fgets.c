/**
 * Example of using fgets to read 10 characters.
 * Try to type 5 characters, 10 characters and more.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>

int main() {
    char buffer[10];

    printf("Type your name: ");
    
    if(fgets(buffer, 10, stdin) == NULL) {
        perror("Error reading characters");
        exit(EXIT_FAILURE);
    }

    printf("Your name: '%s'\n", buffer);

    return EXIT_SUCCESS;
}