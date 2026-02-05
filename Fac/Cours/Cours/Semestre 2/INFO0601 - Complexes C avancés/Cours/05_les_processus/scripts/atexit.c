/**
 * Program that shows how to register methods that will be called at the
 * end of program execution.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>

void method1() {
    printf("I'm in method 1.\n");
}

void method2() {
    printf("I'm in method 2.\n");
}

int main() {
    if(atexit(method1) != 0) {
        perror("Error registring method 1");
        exit(EXIT_FAILURE);
    }
    
    if(atexit(method2) != 0) {
        perror("Error registring method 2");
        exit(EXIT_FAILURE);
    }

    printf("Okay! It's finish.\n");
    
    return EXIT_SUCCESS;
}