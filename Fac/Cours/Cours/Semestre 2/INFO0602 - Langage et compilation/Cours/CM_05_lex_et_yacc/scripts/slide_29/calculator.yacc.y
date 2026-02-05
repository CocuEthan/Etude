%{
#include <stdio.h>
#include <stdlib.h>

int yylex();
void yyerror(const char *error_msg);
%}

%token integer
%left '+'
%left '*'

%%

PROGRAM:
    EXPRESSION '.'
        {
            printf("=%d\n", $1);
        }
    |
    ;

EXPRESSION:
    integer
    | EXPRESSION '+' EXPRESSION
        {
            $$ = $1 + $3;
        }
    | EXPRESSION '*' EXPRESSION
        {
            $$ = $1 * $3;
        }
    ;

%%

int main(void) {
    printf("Enter a simple operation with integers and the operators '+' or '-'\n");
    printf("You must complete the operation with '.' then press CRTL+D\n");
    yyparse();
    return EXIT_SUCCESS;
}