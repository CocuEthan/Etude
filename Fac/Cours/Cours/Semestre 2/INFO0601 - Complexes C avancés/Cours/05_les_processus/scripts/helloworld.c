/**
 * Illustration of getting program arguments.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[], char *argve[]) {
    int i;

    printf("****************\nHello World!!!\n");

    printf("\n Arguments:\n");
    for(i = 0; i < argc; i++) {
        printf("%d: %s\n", i, argv[i]);
    }
    
    printf("\nEnvironment variables:\n");
    i = 0;
    while(argve[i] != NULL) {
        printf("%d : %s\n", i, argve[i]);
        i++;
    }
    if(i == 0)
        printf("No environment variable.\n");
    
    printf("****************\n");

    return EXIT_SUCCESS;
}