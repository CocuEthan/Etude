/**
 * Display error messages.
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

int main() {
    int i;
    
    for(i = 0; i < 100; i++) {
        printf("%d : %s\n", i, strerror(i));
    }
    
    return EXIT_SUCCESS;
}