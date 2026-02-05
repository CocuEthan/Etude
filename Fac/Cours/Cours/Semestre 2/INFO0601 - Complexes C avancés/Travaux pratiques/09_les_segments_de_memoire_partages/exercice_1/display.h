#ifndef _DISPLAY_
#define _DISPLAY_

/**
 * Display grade.
 * @param grade
 */
void display_grade(int grade);

/**
 * Display a digit.
 * @param win the window
 * @param posx the position x
 * @param posy the position y
 * @param score the score
 */
void display_digit(window_t *win, int posx, int posy, int digit);

/**
 * Display score in a window.
 * @param win the window
 * @param posx the position x
 * @param posy the position y
 * @param score the score
 * @param grade the grade
 */
void display_score(window_t *win, int posx, int posy, int score, int grade);

/**
 * Display score in a window.
 * @param win the window
 * @param life the life
 */
void display_life(window_t *win, int life);

#endif