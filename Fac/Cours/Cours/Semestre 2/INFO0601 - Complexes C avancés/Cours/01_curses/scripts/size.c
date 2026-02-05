/**
 * Get the dimensions of the terminal in ncurses with COLS and LINES constants.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
  
  printw("The terminal size is (%d,%d)...", COLS, LINES);
  
  // Wait for a key
  getch();

  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}