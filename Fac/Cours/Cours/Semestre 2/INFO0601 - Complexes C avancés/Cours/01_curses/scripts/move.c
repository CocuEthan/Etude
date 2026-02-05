/**
 * Move a character on screen with arrow keys.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  int posX, posY, ch;
    
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
    
  // Center position
  posX = COLS / 2 - 1;
  posY = LINES / 2 - 1;
  
  // Display character
  printw("Move the diamond with arrow keys and press F2 to quit");
  mvaddch(posY, posX, ACS_DIAMOND);
  
  // Main loop : F2 to stop
  while((ch = getch()) != KEY_F(2)) {
    // Erase the character
    mvaddch(posY, posX, ' ');
    
    // New position
    switch(ch) {
      case KEY_LEFT:
        if(posX > 0)
          posX--;
        break;
      case KEY_RIGHT:
        if(posX < COLS - 1)
          posX++;
        break;
      case KEY_UP:
        if(posY > 1)
          posY--;
        break;
      case KEY_DOWN:
        if(posY < LINES - 1)
          posY++;
        break;
    }
    
    // Display character
    mvaddch(posY, posX, ACS_DIAMOND);
  }

  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}