/**
 * Trying functions for display.
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
  
  move(5, 5);
  printw("A bold character: ");
  addch('A' | A_BOLD);
  
  move(7, 5);
  printw("An underline character: ");
  addch('B' | A_UNDERLINE);
  
  move(9, 5);
  printw("I can display data (an integer %d or a float %f) like the classic printf...", 12, 0.5);
  
  mvprintw(11, 5, "And I can move where I want");
  
  attron(A_BOLD);
  mvprintw(13, 5, "A bold character string !");
  attroff(A_BOLD);
  
  // Waiting a key press
  move(LINES - 1, 0);
  printw("Press a key...");
  getch();

  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}