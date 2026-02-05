/**
 * Using mouse in ncurses.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  int ch, posX, posY;
    
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
  ncurses_init_mouse();
  
  // Main loop
  printw("Click in the terminal with the mouse - 'Q' to quit");
  while(((ch = getch()) != 'Q') && (ch != 'q')) {
    switch(ch) {
      case KEY_MOUSE:
        if(mouse_getpos(&posX, &posY) == OK) {
          move(LINES - 1, 2);
          clrtoeol();
          printw("Click at (%d, %d)", posX, posY);
        }
    }
  }

  // stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}