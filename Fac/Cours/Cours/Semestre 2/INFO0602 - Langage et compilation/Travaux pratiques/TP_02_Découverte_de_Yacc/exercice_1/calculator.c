#include <stdlib.h>

extern int yyparse();

int main(int argc, char *argv[]) {
    yyparse();
    return EXIT_SUCCESS;
}