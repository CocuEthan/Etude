EXECUTABLE = example

LEX = flex
LEXFLAGS = 
LEXLIB = -lfl

$(EXECUTABLE): lex.yy.o
	gcc -o $(EXECUTABLE) lex.yy.o $(LEXLIB) -W -Wall

lex.yy.o: lex.yy.c
	gcc -c lex.yy.c -W -Wall -Werror

lex.yy.c: $(EXECUTABLE:=.lex)
	$(LEX) $(LEXFLAGS) $(EXECUTABLE:=.lex) 

clean:
	rm -f *~ \#* *.o
	rm -f $(EXECUTABLE) $(EXECUTABLE:=.exe)
	rm -f *.core *.stackdump
	rm -f lex.yy.c lex.yy.o
