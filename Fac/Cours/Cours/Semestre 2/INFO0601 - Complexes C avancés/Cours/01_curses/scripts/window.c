/**
 * Create a window without scrolling.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  int i;
  WINDOW *window;
  
  // ncurses initialisation
  setlocale(LC_ALL, "");
  ncurses_init();
  
  // Create window
  window = newwin(10, 10, 5, 20);
  
  // Display in the window
  printw("Press key to go to next step (15 times)");
  for(i = 0; i < 15; i++) {
    wprintw(window, "Hello %d\n", i);
    wrefresh(window);
    getch();
  }  

  // Delete window and stop ncurses
  delwin(window);
  ncurses_stop();

  return EXIT_SUCCESS;
}