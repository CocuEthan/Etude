#include <stdio.h>
#include <stdlib.h>
#include <ncurses.h>
#include <locale.h>
#include <string.h>
#include <unistd.h>
#include <sys/shm.h>
#include <sys/stat.h>

#include "functions.h"
#include "window.h"
#include "colors.h"
#include "include.h"
#include "display.h"

/**
 * Main function.
 * @param argc the number of arguments
 * @param argv arguments
 * @return the return code
 */
int main(int argc, char *argv[]) {
    bool stop = FALSE;
    window_t *win_map, *win_infos, *win_score, *win_life;
    int n, i, j, posX, posY, x, y, score = 0, grade = 0, life = 100;
    unsigned char *map;
    
    // #TODO# #1 delete this instruction
    map = malloc(sizeof(unsigned char) * WIDTH * HEIGHT);
    
    // Get the shared memory segment and attach it
    // #TODO# #2 create and attach segment
    
    // Initialize the map
    memset(map, ' ', sizeof(unsigned char) * WIDTH * HEIGHT);
    
    // Initialize ncurses
    ncurses_init();
    ncurses_init_mouse();
    ncurses_colors(); 
    palette();
    clear();
    refresh();
    timeout(1000);
    
    // Check the terminal dimensions
    if((COLS < WIDTH + 20) || (LINES < HEIGHT + 9)) {
        ncurses_stop();
        fprintf(stderr, 
              "Dimensions are invalid (%d,%d). width must be greater than %d and height mut be greater than %d\n",
              COLS, LINES, WIDTH + 2, HEIGHT + 9);
        exit(EXIT_FAILURE);
    }
    
    // Create windows
    win_infos = window_create(0, 0, COLS, 7, "Informations", TRUE);
    win_map = window_create(0, 7, WIDTH + 2, HEIGHT + 2, "Body map", FALSE);    
    window_printw(win_infos, "Click on viruses to destroy them.");
    window_printw(win_infos, "\nPress 'S' to leave this cruel world.");
    window_refresh(win_infos);
    win_score = window_create(WIDTH + 2, 7, 15, 11, "Score", FALSE);
    display_score(win_score, 1, 1, score, grade);
    win_life = window_create(WIDTH + 2, 18, 18, 5, "Life", FALSE);
    display_life(win_life, life);
    
    // Main loop
    while((stop == FALSE) && (n = getch())) {
        switch(n) {
            case 's':
            case 'S':
                stop = TRUE;
                break;
            case KEY_MOUSE:
                if(mouse_getpos(&posX, &posY) == OK) {
                    if(window_getcoordinates(win_map, posX, posY, &x, &y) == TRUE) {
                        if(map[y * WIDTH + x] != ' ') {
                            score += 3;
                            window_printw(win_infos, "\nYou destroy a virus.");
                        }
                        else {
                            window_printw(win_infos, "\nMiss clic.");
                            if(score > 0)
                                score--;
                        }
                        grade = score / 50;
                        if(grade > 11)
                            grade = 11;
                        display_score(win_score, 1, 1, score, grade);
                        window_refresh(win_infos);
                        map[y * WIDTH + x] = ' ';
                    }
                }
                // No break to refresh the map
            case ERR:
                // We refresh the map
                window_move(win_map, 0, 0);
                j = 0;
                for(i = 0; i < HEIGHT * WIDTH; i++) {
                    window_addch_col(win_map, RED, map[i]);
                    if(map[i] != ' ')
                        j++;
                }
                if(j > LIMIT) {
                    life--;
                    if(life < 0) {
                        life = 0;
                        stop = TRUE;
                    }
                    display_life(win_life, life);
                }
                    
                window_refresh(win_map);
                window_refresh(win_infos);
                break;
        }        
    }
    
    // Arrêt de ncurses
    window_delete(&win_map);
    window_delete(&win_infos);
    window_delete(&win_score);
    window_delete(&win_life);
    ncurses_stop();
    
    // Detach segment
    // #TODO# #3 detach segment
    
    // Delete segment
    // #TODO# #4 delete segment

    // End message
    if(life == 0)
        printf("You lose!\n");
    printf("Score: %d Grade: ", score);
    display_grade(grade);
    printf("\n");

    // #TODO# #5 delete this instruction
    free(map);

    return EXIT_SUCCESS;    
}