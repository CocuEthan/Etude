%{
#include <stdio.h>
#include <stdlib.h>

void yyerror(const char *error_msg);
int yylex();
%}

%token integer

%%

EXEC: EXPRESSION '.' {
           printf("=%d\n", $1);
      }
      |
      ;

EXPRESSION: integer
      | EXPRESSION '+' EXPRESSION {
        $$ = $1 + $3;
      }
      | EXPRESSION '-' EXPRESSION {
        $$ = $1 - $3;
      };

%%
