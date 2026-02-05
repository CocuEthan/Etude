%{
#include <stdio.h>
#include <stdlib.h>

int yylex();
void yyerror(const char *erreurMsg);
%}

%token integer

%%

EXPRESSION:
    integer
    | EXPRESSION '+' EXPRESSION
    | EXPRESSION '*' EXPRESSION
    ;

%%

int main(void) {
    printf("Enter a simple operation with two integers and the operators '+' or '*'\n");
    printf("A second operation generates an error.\n");
    yyparse();
    return EXIT_SUCCESS;
}