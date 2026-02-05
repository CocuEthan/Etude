/**
 * Read 2 strings with `scanf` (try to type a string with spaces).
 * @author Cyril Rabat
 */
#include <stdio.h>
#include <stdlib.h>

int main() {
    char s1[10];
    char s2[10];
    char c;

    printf("Type your lastname: ");
    if(scanf("%9s", s1) != 1) {
        fprintf(stderr, "scanf error\n");
        exit(EXIT_FAILURE);
    }
    while(((c = getchar()) != '\n') || (c == EOF));

    printf("Type your firstname: ");
    if(scanf("%9s", s2) != 1) {
        fprintf(stderr, "scanf error\n");
        exit(EXIT_FAILURE);
    }  
    while(((c = getchar()) != '\n') || (c == EOF));
    
    printf("Lastname: %s Firstname: %s\n", s1, s2);

    return EXIT_SUCCESS;
}