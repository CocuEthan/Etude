EXECUTABLE = calculator

CFLAGS = -W -Wall -Werror

LEX = flex
LEXFLAGS = 
LEXLIB = -lfl

YACC = yacc
YACCFLAGS = -d
YACCLIB = 

$(EXECUTABLE): y.tab.o lex.yy.o
	gcc -o $(EXECUTABLE) y.tab.o lex.yy.o $(LEXLIB) $(YACCLIB)

y.tab.o : y.tab.h y.tab.c
	gcc -c y.tab.c $(CFLAGS)

y.tab.c y.tab.h : calculator.yacc.y
	$(YACC) $(YACCFLAGS) $(EXECUTABLE:=.yacc.y)

lex.yy.o : lex.yy.c y.tab.h
	gcc -c lex.yy.c $(CFLAGS)

lex.yy.c : $(EXECUTABLE:=.lex) y.tab.h
	$(LEX) $(LEXFLAGS) $(EXECUTABLE:=.lex)

clean:
	rm -f y.tab.*
	rm -f lex.yy.*
	rm -f $(EXECUTABLE) $(EXECUTABLE:=.exe)
	rm -f *.core *.stackdump