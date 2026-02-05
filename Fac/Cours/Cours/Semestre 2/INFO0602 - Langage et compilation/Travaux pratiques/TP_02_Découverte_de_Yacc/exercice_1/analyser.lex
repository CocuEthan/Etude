%{
#include "y.tab.h" 
void yyerror(const char *error_msg);

extern int yylval;
%}

/* To avoid warnings on input and yyunput */
%option nounput
%option noinput

%%

[0-9]+	 {
        yylval = atoi(yytext);
        return integer;
    }
[-+\.]	 return *yytext;
[[:space:]]	 ;
.        yyerror("Invalid character");

%%

void yyerror(const char *error_msg) {
    fprintf(stderr, "\n Error '%s' on '%s'.\n", error_msg, yytext);
    exit(EXIT_FAILURE);
}