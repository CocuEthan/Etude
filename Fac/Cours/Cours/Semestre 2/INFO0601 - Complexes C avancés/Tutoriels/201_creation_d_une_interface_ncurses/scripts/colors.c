#include "colors.h"

#include <ncurses.h>

/**
 * Palette definition.
 */
void palette() {
    init_pair(WHITE, COLOR_WHITE, COLOR_BLACK);
    init_pair(GREEN, COLOR_GREEN, COLOR_BLACK);
    init_pair(BLUE, COLOR_BLUE, COLOR_BLACK);
    init_pair(RED, COLOR_RED, COLOR_BLACK);
    init_pair(YELLOW, COLOR_YELLOW, COLOR_BLACK);
    init_pair(CYAN, COLOR_CYAN, COLOR_BLACK);
    init_pair(MAGENTA, COLOR_MAGENTA, COLOR_BLACK);
    init_pair(BK_WHITE, COLOR_BLACK, COLOR_WHITE);
    init_pair(BK_GREEN, COLOR_BLACK, COLOR_GREEN);
    init_pair(BK_BLUE, COLOR_BLACK, COLOR_BLUE);
    init_pair(BK_RED, COLOR_BLACK, COLOR_RED);
    init_pair(BK_YELLOW, COLOR_BLACK, COLOR_YELLOW);
    init_pair(BK_CYAN, COLOR_BLACK, COLOR_CYAN);
    init_pair(BK_MAGENTA, COLOR_BLACK, COLOR_MAGENTA);
}