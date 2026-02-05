/**
 * Overlay of two windows.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  int i, j;
  WINDOW *window1, *window2;
  
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
  printw("Press a key to go to the next step");
  
  // Create and fill the first window
  window1 = newwin(10, 15, 10, 2);
  box(window1, 0, 0);
  for(i = 1; i < 9; i++)
    for(j = 1; j < 14; j++)
      mvwaddch(window1, i, j, 'X');
  wrefresh(window1);
  
  // Create the second window
  window2 = newwin(6, 11, 12, 4);
  box(window2, 0, 0);
  wrefresh(window2);
  getch();
  
  // Place window 1 over window 2
  touchwin(window1);
  wrefresh(window1);
  getch();
  
  // Place window 2 over window 1
  touchwin(window2);
  wrefresh(window2);
  getch();
  
  // Delete windows
  delwin(window1);
  delwin(window2);

  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}