%{
#include <stdio.h>
#include <stdlib.h>

int num_row = 1;
%}

/* To avoid warnings on input and yyunput */
%option nounput
%option noinput

DIGIT   [0-9]
/* you can just use [:digit:] class */
INTEGER {DIGIT}+
/* or INTEGER [0-9]+ */
FLOAT   {INTEGER}(\.{INTEGER}+)?
/* or FLOAT [0-9]+(\.[0-9]+)? */

%%

{INTEGER}   printf("Integer %d\n", atoi(yytext));
{FLOAT}     printf("Float %f\n", atof(yytext));
\n          num_row++;
.           ECHO;

%%

int main() {
    printf("Type integers or floats and ENTER to validate. To exit, pressez CRTL+D (or CRTL+C)\n");
    yylex();
    return EXIT_SUCCESS;
}