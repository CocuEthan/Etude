#include <stdlib.h>

extern int yylex();

int main(int argc, char *argv[]) {
    yylex();
    return EXIT_SUCCESS;
}