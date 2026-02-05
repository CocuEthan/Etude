/**
 * buffer overflow example with `scanf`.
 * Type a lot of characters.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>

int main() {
    char *s = (char*)malloc(sizeof(char) * 10);

    if(s == NULL) {
        perror("Allocation error");
        exit(EXIT_FAILURE);
    }
    printf("Type your name (type (much) more than 10 characters: ");
    if(scanf("%s", s) != 1) {
        fprintf(stderr, "Scanf error\n");
        exit(EXIT_FAILURE);
    }
    printf("Entered string: %s\n", s);
    free(s);

    return EXIT_SUCCESS;
}