/**
 * Use of colors in ncurses.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

/**
 * Palette definition
 */
void palette() {    
  init_pair(1, COLOR_BLUE, COLOR_BLACK);
  init_pair(2, COLOR_RED, COLOR_BLACK);
  init_pair(3, COLOR_GREEN, COLOR_BLACK);
}

int main() {
  int i;
    
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
  
  // Colors initialisation and palette definition
  ncurses_colors();
  palette();
  
  // Display examples
  for(i = 1; i <= 3; i++) {
    attron(COLOR_PAIR(i));
    printw("Hello %d\n", i);
    attroff(COLOR_PAIR(i));
  }

  // Waiting
  move(LINES - 1, 0);
  printw("Press a key...");
  getch();

  // ncurses stop
  ncurses_stop();

  return EXIT_SUCCESS;
}