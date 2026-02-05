#include <stdlib.h>

#include "window.h"

/**
 * Create a new window.
 * @param[in] posX X position of the window
 * @param[in] posY Y position of the window
 * @param[in] width the window width
 * @param[in] height the window height
 * @param[in] title the window title
 * @param[in] scroll if 'TRUE' active the scrolling
 * @return the created window
 */
window_t *window_create(int posX, int posY, int width, int height, char *title, bool scroll) {
    window_t *result;   

    // Structure allocation
    if((result = malloc(sizeof(window_t))) == NULL) {
        fprintf(stderr, "Error allocation window\n");
        exit(EXIT_FAILURE);
    }

    // Filling fields
    result->posx = posX;
    result->posy = posY;
    result->height = height;
    result->width = width;

    // Create main window with the box
    result->box = newwin(height, width, posY, posX);
    box(result->box, 0, 0);
    wprintw(result->box, "%s", title);
    wrefresh(result->box);

    // Create inner window
    result->inner = subwin(result->box, height - 2, width - 2, posY + 1, posX + 1);
    scrollok(result->inner, scroll);
    wrefresh(result->inner);

    return result;
}

/**
 * Delete a window.
 * @param[in,out] window the window to delete
 */
void window_delete(window_t **window) {
  delwin((*window)->inner);
  delwin((*window)->box);
  free(*window);
  *window = NULL;
}

/**
 * Check if a global position is in a window.
 * @param[in] the window
 * @param[in] x the X position
 * @param[in] y the Y position
 * @return TRUE if the position is in the window
 */
bool window_isin(window_t *window, int x, int y) {
  bool result = FALSE;

  if(((x >= window->posx + 1) && (x < window->width + window->posx - 1)) &&
     ((y >= window->posy + 1) && (y < window->height + window->posy - 1)))
    result = TRUE;

  return result;
}

/**
 * Get the window position of a global position.
 * @param[in] the window
 * @param[in] posX the global X position
 * @param[in] posY the global Y position
 * @param[out] x the X position in the window
 * @param[out] y the Y position in the window
 * @return TRUE if the position is in the window
 */
bool window_getcoordinates(window_t *window, int posx, int posy, int *x, int *y) {
  bool result = FALSE;

  if(((posx >= window->posx + 1) && (posx < window->width + window->posx - 1)) &&
     ((posy >= window->posy + 1) && (posy < window->height + window->posy - 1))) {
    result = TRUE;
    *x = posx - window->posx - 1;
    *y = posy - window->posy - 1;
  }

  return result;
}

/**
 * Move the cursor of the window to (posY,posX) position
 * @param[in] window the window 
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @return OK on success
 */
int window_move(window_t *window, int posY, int posX) {
    return wmove(window->inner, posY, posX);
}

/**
 * Put a character at the window current position.
 * @param[in] window the window
 * @param[in] c the character to put
 * @return OK on success
 */
int window_addch(window_t *window, chtype c) {
    return waddch(window->inner, c);
}

/**
 * Put a character in the window at the specified position.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] c the character to put
 * @return OK on success
 */
int window_mvaddch(window_t *window, int posY, int posX, chtype c) {
    wmove(window->inner, posY, posX);
    return waddch(window->inner, c);
}

/**
 * Put a character at the window current position in the specified color.
 * @param[in] window the window
 * @param[in] color the color
 * @param[in] c the character to put
 * @return OK on success
 */
int window_addch_col(window_t *window, unsigned int color, chtype c) {
    int result;
    
    wattron(window->inner, COLOR_PAIR(color));
    result = waddch(window->inner, c);
    wattroff(window->inner, COLOR_PAIR(color));
    
    return result;
}

/**
 * Put a character in the window at the specified position in the specified color.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] color the color
 * @param[in] c the character to put
 * @return OK on success
 */
int window_mvaddch_col(window_t *window, int posY, int posX, unsigned int color, chtype c) {
    int result;
    
    wattron(window->inner, COLOR_PAIR(color));
    wmove(window->inner, posY, posX);
    result = waddch(window->inner, c);
    wattroff(window->inner, COLOR_PAIR(color));
    
    return result;
}

/**
 * printf in ncurses mode.
 * @param[in] window the window
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_printw(window_t *window, const char *fmt, ...) {
    va_list lstPar;
    int result;
    
    va_start(lstPar, fmt);
    result = vw_printw(window->inner, fmt, lstPar);
    va_end(lstPar);
    
    return result;
}

/**
 * printf in ncurses mode in the specified color.
 * @param[in] window the window
 * @param[in] color the color
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_printw_col(window_t *window, unsigned int color, const char *fmt, ...) {
    va_list lstPar;
    int result;
    
    va_start(lstPar, fmt);
    wattron(window->inner, COLOR_PAIR(color));
    result = vw_printw(window->inner, fmt, lstPar);
    wattroff(window->inner, COLOR_PAIR(color));
    va_end(lstPar);
    
    return result;
}

/**
 * printf in ncurses mode at the specified position.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_mvprintw(window_t *window, int posY, int posX, const char *fmt, ...) {
    va_list lstPar;
    int result;
    
    va_start(lstPar, fmt);
    wmove(window->inner, posY, posX);
    result = vw_printw(window->inner, fmt, lstPar);
    va_end(lstPar);
    
    return result;    
}

/**
 * printf in ncurses mode at the specified position in the specified color.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] color the color
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_mvprintw_col(window_t *window, int posY, int posX, unsigned int color, const char *fmt, ...) {
    va_list lstPar;
    int result;
    
    va_start(lstPar, fmt);
    wmove(window->inner, posY, posX);
    wattron(window->inner, COLOR_PAIR(color));
    result = vw_printw(window->inner, fmt, lstPar);
    wattroff(window->inner, COLOR_PAIR(color));
    va_end(lstPar);
    
    return result;    
}

/**
 * Refresh the window.
 * @param[in] window the window
 * @return OK on success
 */
int window_refresh(window_t *window) {
    return wrefresh(window->inner);
}

/**
 * Change the current color of the window.
 * @param[in] window the window
 * @param[in] color the color
 * @return OK on success
 */
int window_color(window_t *window, unsigned int color) {
    return wattron(window->inner, COLOR_PAIR(color));
}

/**
 * Erase the window content.
 * @param[in] window the window
 * @return OK on success
 */
int window_erase(window_t *window) {
    return werase(window->inner);
}