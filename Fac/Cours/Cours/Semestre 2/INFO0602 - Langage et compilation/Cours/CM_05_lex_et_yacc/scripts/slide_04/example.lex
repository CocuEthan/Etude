%{
#include <stdio.h>
#include <stdlib.h>

int num_row = 1;
%}

/* To avoid warnings on input and yyunput */
%option nounput
%option noinput

DIGIT [0-9]

%%

{DIGIT}     printf("Digit '%s' (on line %d)\n", yytext, num_row);
\n          num_row++;
.           ;

%%

int main() {
    printf("Type characters (letters or digits) and ENTER to validate. To exit, pressez CRTL+D (or CRTL+C)\n");
    yylex();
    return EXIT_SUCCESS;
}