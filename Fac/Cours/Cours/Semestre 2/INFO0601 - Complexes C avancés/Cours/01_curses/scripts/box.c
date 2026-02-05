/**
 * Create a window with a box.
 * @author Cyril Rabat
 **/
#include <locale.h>
#include <stdlib.h>
#include <ncurses.h>

#include "functions.h"

int main() {
  int i = 0;
  WINDOW *window, *subwindow;
  
  // Initialisation de ncurses
  setlocale(LC_ALL, "");
  ncurses_init();
  printw("Press a key to go to the next step");
  
  // Create the main window with a box
  window = newwin(10, 15, 10, 2);
  box(window, 0, 0);
  mvwprintw(window, 0, 1, " Title ");
  
  // Create the subwindow
  subwindow = subwin(window, 8, 13, 11, 3);
  scrollok(subwindow, TRUE);
  wrefresh(window);
  wrefresh(subwindow);
  
  // Display
  wprintw(subwindow, "Hello %d", i);
  wrefresh(subwindow);
  getch();
  for(i = 1; i < 15; i++) {
    wprintw(subwindow, "\nDisplay %d", i);
    wrefresh(subwindow);
    getch();
  }  
  
  // Delete windows
  delwin(subwindow);
  delwin(window);

  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}