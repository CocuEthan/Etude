/**
 * Display ncurses special chars.
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
  
  printw("ACS_ULCORNER : ");addch(ACS_ULCORNER);
  printw(" ACS_LLCORNER : ");addch(ACS_LLCORNER);
  printw(" ACS_URCORNER : ");addch(ACS_URCORNER);
  printw(" ACS_LRCORNER : ");addch(ACS_LRCORNER);
  printw("\n\nACS_LTEE     : ");addch(ACS_LTEE);
  printw(" ACS_RTEE     : ");addch(ACS_RTEE);
  printw(" ACS_BTEE     : ");addch(ACS_BTEE);
  printw(" ACS_TTEE     : ");addch(ACS_TTEE);
  printw("\n\nACS_HLINE    : ");addch(ACS_HLINE);
  printw(" ACS_VLINE    : ");addch(ACS_VLINE);
  printw(" ACS_PLUS     : ");addch(ACS_PLUS);
  printw(" ACS_BULLET   : ");addch(ACS_BULLET);
  printw("\n\nACS_S1       : ");addch(ACS_S1);
  printw(" ACS_S3       : ");addch(ACS_S3);
  printw(" ACS_S7       : ");addch(ACS_S7);
  printw(" ACS_S9       : ");addch(ACS_S9);
  printw("\n\nACS_DIAMOND  : ");addch(ACS_DIAMOND);
  printw(" ACS_CKBOARD  : ");addch(ACS_CKBOARD);
  printw(" ACS_DEGREE   : ");addch(ACS_DEGREE);
  printw(" ACS_PLMINUS  : ");addch(ACS_PLMINUS);
  printw("\n\nACS_LARROW   : ");addch(ACS_LARROW);
  printw(" ACS_RARROW   : ");addch(ACS_RARROW);
  printw(" ACS_DARROW   : ");addch(ACS_DARROW);
  printw(" ACS_UARROW   : ");addch(ACS_UARROW);
  printw("\n\nACS_BOARD    : ");addch(ACS_BOARD);
  printw(" ACS_LANTERN  : ");addch(ACS_LANTERN);
  printw(" ACS_BLOCK    : ");addch(ACS_BLOCK);
  printw(" ACS_LEQUAL   : ");addch(ACS_LEQUAL);
  printw("\n\nACS_GEQUAL   : ");addch(ACS_GEQUAL);
  printw(" ACS_PI       : ");addch(ACS_PI);
  printw(" ACS_NEQUAL   : ");addch(ACS_NEQUAL);
  printw(" ACS_STERLING : ");addch(ACS_STERLING);
  
  printw("\n\nPress a key to quit...");
  refresh();  
  getch();
  
  // Stop ncurses
  ncurses_stop();

  return EXIT_SUCCESS;
}