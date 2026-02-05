#
# MAIN CONFIGURATION
#

EXEC = pointers sizes scanf1 scanf2 fgets initializations structure1 structure2 stringstorage1 stringstorage2 stringstorage3 structuresize1 structurestorage1 structuresize2 structurestorage2 structurestorage3 speed1 speed2
OBJECTS = 
PROJECT_NAME = C_complements_course

#
# SUFFIXES
#

.SUFFIXES: .c .o

#
# OBJECTS
#

EXEC_O = $(EXEC:=.o)
OBJECTS_O = $(OBJECTS) $(EXEC_O)

#
# ARGUMENTS AND COMPILER
#

CC = gcc
CCFLAGS_STD = -Wall -Werror
CCFLAGS_DEBUG = -D _DEBUG_
CCFLAGS = $(CCFLAGS_STD)
CCLIBS = 

#
# RULES
#

all: msg $(OBJECTS) $(EXEC_O)
	@echo "Create executables..."
	@for i in $(EXEC); do \
	$(CC) -o $$i $$i.o $(OBJECTS) $(CCLIBS); \
	done
	@echo "Done."

msg:
	@echo "Create objects..."

debug: CCFLAGS = $(CCFLAGS_STD) $(CCFLAGS_DEBUG)
debug: all

#
# DEFAULT RULES
#

%.o : %.c
	@cd $(dir $<) && ${CC} ${CCFLAGS} -c $(notdir $<) -o $(notdir $@)

#
# GENERAL RULES
#

clean:
	@echo "Delete objects, temporary files..."
	@rm -f $(OBJECTS) $(EXEC_O)
	@rm -f *~ *#
	@rm -f $(EXEC)
	@rm -f dependancies
	@echo "Done."

depend:
	@echo "Create dependancies..."
	@sed -e "/^# DEPENDANCIES/,$$ d" makefile > dependancies
	@echo "# DEPENDANCIES" >> dependancies
	@for i in $(OBJECTS_O); do \
	$(CC) -MM -MT $$i $(CCFLAGS) `echo $$i | sed "s/\(.*\)\\.o$$/\1.c/"` >> dependancies; \
	done
	@cat dependancies > makefile
	@rm dependancies
	@echo "Done."

#
# CREATE ARCHIVE
#

ARCHIVE_FILES = *

archive: clean
	@echo "Create archive $(PROJECT_NAME)_$(shell date '+%y%m%d.tar.gz')..."
	@REP=`basename "$$PWD"`; cd .. && tar zcf $(PROJECT_NAME)_$(shell date '+%y%m%d.tar.gz') $(addprefix "$$REP"/,$(ARCHIVE_FILES))
	@echo "Done."

# DEPENDANCIES
pointers.o: pointers.c
sizes.o: sizes.c
scanf1.o: scanf1.c
scanf2.o: scanf2.c
fgets.o: fgets.c
initializations.o: initializations.c
structure1.o: structure1.c
structure2.o: structure2.c
stringstorage1.o: stringstorage1.c
stringstorage2.o: stringstorage2.c
stringstorage3.o: stringstorage3.c
structuresize1.o: structuresize1.c
structurestorage1.o: structurestorage1.c
structuresize2.o: structuresize2.c
structurestorage2.o: structurestorage2.c
structurestorage3.o: structurestorage3.c
speed1.o: speed1.c
speed2.o: speed2.c
