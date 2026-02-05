%{
#include "y.tab.h" 

extern int yylval;
void yyerror(const char *error_msg);
%}

%%

[0-9]+	 {
           yylval = atoi(yytext);
           return integer;
         }
[+*]	 { return yytext[0]; }
[ \t\n]	 ; 
.        yyerror("Invalid character");

%%

void yyerror(const char *error_msg) {
    fprintf(stderr, "\n Error '%s' on '%s'.\n", error_msg, yytext);
    exit(EXIT_FAILURE);
}