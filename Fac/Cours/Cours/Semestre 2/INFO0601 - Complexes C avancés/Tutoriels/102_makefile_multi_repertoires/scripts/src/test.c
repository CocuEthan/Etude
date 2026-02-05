#include <stdio.h>
#include <stdlib.h>

#include "example.h"

int main() {
    char str[256];
    
    printf("Please, type a word: ");
    if(scanf("%255s", str) != 1) {
        fprintf(stderr, "No word...\n");
        exit(EXIT_FAILURE);
    }
    
#ifdef _DEBUG_
    printf("#DEBUG# - Here's Johnny\n");
#endif
    
    hello(str);
    
    return EXIT_SUCCESS;
}