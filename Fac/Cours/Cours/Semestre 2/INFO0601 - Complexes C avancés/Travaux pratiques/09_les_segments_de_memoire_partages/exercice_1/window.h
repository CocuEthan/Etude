#ifndef _WINDOW_
#define _WINDOW_

#include <ncurses.h>

// Structure of a window with its box and inner subwindow
typedef struct {
    int posx, posy;
    int width, height;
    WINDOW *box;
    WINDOW *inner;
} window_t;

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
window_t *window_create(int posX, int posY, int width, int height, char *title, bool scroll);

/**
 * Delete a window.
 * @param[in,out] window the window to delete
 */
void window_delete(window_t **window);

/**
 * Check if a global position is in a window.
 * @param[in] the window
 * @param[in] x the X position
 * @param[in] y the Y position
 * @return TRUE if the position is in the window
 */
bool window_isin(window_t *window, int x, int y);

/**
 * Get the window position of a global position.
 * @param[in] the window
 * @param[in] posX the global X position
 * @param[in] posY the global Y position
 * @param[out] x the X position in the window
 * @param[out] y the Y position in the window
 * @return TRUE if the position is in the window
 */
bool window_getcoordinates(window_t *window, int posx, int posy, int *x, int *y);

/**
 * Move the cursor of the window to (posY,posX) position
 * @param[in] window the window 
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @return OK on success
 */
int window_move(window_t *window, int posY, int posX);

/**
 * Put a character at the window current position.
 * @param[in] window the window
 * @param[in] c the character to put
 * @return OK on success
 */
int window_addch(window_t *window, chtype c);

/**
 * Put a character in the window at the specified position.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] c the character to put
 * @return OK on success
 */
int window_mvaddch(window_t *window, int posY, int posX, chtype c);

/**
 * Put a character at the window current position in the specified color.
 * @param[in] window the window
 * @param[in] color the color
 * @param[in] c the character to put
 * @return OK on success
 */
int window_addch_col(window_t *window, unsigned int color, chtype c);

/**
 * Put a character in the window at the specified position in the specified color.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] color the color
 * @param[in] c the character to put
 * @return OK on success
 */
int window_mvaddch_col(window_t *window, int posY, int posX, unsigned int color, chtype c);

/**
 * printf in ncurses mode.
 * @param[in] window the window
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_printw(window_t *window, const char *fmt, ...);

/**
 * printf in ncurses mode in the specified color.
 * @param[in] window the window
 * @param[in] color the color
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_printw_col(window_t *window, unsigned int color, const char *fmt, ...);

/**
 * printf in ncurses mode at the specified position.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_mvprintw(window_t *window, int posY, int posX, const char *fmt, ...);

/**
 * printf in ncurses mode at the specified position in the specified color.
 * @param[in] window the window
 * @param[in] posY the Y position
 * @param[in] posX the X position
 * @param[in] color the color
 * @param[in] fmt the printf format
 * @return OK on success
 */
int window_mvprintw_col(window_t *window, int posY, int posX, unsigned int color, const char *fmt, ...);

/**
 * Refresh the window.
 * @param[in] window the window
 * @return OK on success
 */
int window_refresh(window_t *window);

/**
 * Change the current color of the window.
 * @param[in] window the window
 * @param[in] color the color
 * @return OK on success
 */
int window_color(window_t *window, unsigned int color);

/**
 * Erase the window content.
 * @param[in] window the window
 * @return OK on success
 */
int window_erase(window_t *window);

#endif