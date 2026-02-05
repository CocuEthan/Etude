#include "window.h"
#include "colors.h"
#include "display.h"

const unsigned char digits[10][5][3] = {
        { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 0, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },
        { { 1, 1, 0 }, { 0, 1, 0 }, { 0, 1, 0 }, { 0, 1, 0 }, { 1, 1, 1 } },
        { { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 } },
        { { 1, 1, 1 }, { 0, 0, 1 }, { 0, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } },
        { { 1, 0, 0 }, { 1, 0, 0 }, { 1, 1, 1 }, { 0, 0, 1 }, { 0, 0, 1 } },
        { { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } },
        { { 1, 1, 1 }, { 1, 0, 0 }, { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },
        { { 1, 1, 1 }, { 0, 0, 1 }, { 0, 0, 1 }, { 0, 0, 1 }, { 0, 0, 1 } },
        { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 } },
        { { 1, 1, 1 }, { 1, 0, 1 }, { 1, 1, 1 }, { 0, 0, 1 }, { 1, 1, 1 } }
    };

const char *grades[] = {
        "   Noob    ",
        " Externe 1 ",
        " Externe 2 ",
        " Externe 3 ",
        " Interne 1 ",
        " Interne 2 ",
        " Interne 3 ",
        "  Docteur  ",
        "Professeur ",
        "Pr. Raoult ",
        "L. Pasteur ",
        " Dr. House "
    };   

/**
 * Display grade.
 * @param grade
 */
void display_grade(int grade) {
    printf("%s", grades[grade]);
}

/**
 * Display a digit.
 * @param win the window
 * @param posx the position x
 * @param posy the position y
 * @param score the score
 */
void display_digit(window_t *win, int posx, int posy, int digit) {
    int i, j;
    
    for(i = 0; i < 3; i++) {
        for(j = 0; j < 5; j++) {
            if(digits[digit][j][i] == 0)
                window_mvaddch_col(win, posy+j, posx+i, YELLOW, ' ');
            else
                window_mvaddch_col(win, posy+j, posx+i, BK_YELLOW, ' ');
        }
    }
}

/**
 * Display score in a window.
 * @param win the window
 * @param posx the position x
 * @param posy the position y
 * @param score the score
 * @param grade the grad
 */
void display_score(window_t *win, int posx, int posy, int score, int grade) {
    if(score > 999)
        score = score % 1000;
    display_digit(win, posx, posy, score / 100);
    score = score % 100;
    display_digit(win, posx + 4, posy, score / 10);
    score = score % 10;
    display_digit(win, posx + 8, posy, score);
    window_mvprintw(win, posy + 6, posx, grades[grade]);
    window_refresh(win);
}

/**
 * Display score in a window.
 * @param win the window
 * @param life the life
 */
void display_life(window_t *win, int life) {
    int i, n = life / 10;
    
    window_move(win, 1, 1);
    window_printw(win, "%3d ", life);
    
    for(i = 0; i < n; i++)
        window_addch_col(win, BK_RED, ' ');
    
    for(i = n; i < 10; i++)
        window_addch_col(win, RED, ' ');
    
    window_refresh(win);
}