#include <stdio.h>
#include <stdlib.h>
#include <ncurses.h>
#include <locale.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

#include "functions.h"
#include "window.h"
#include "colors.h"
#include "include.h"

/**
 * Returns a random integer in intervalle [a, b].
 * @param a the lower bound
 * @param b the upper bound
 * @return a random integer
 */
int random_integer(int a, int b) {
    return rand() % (b - a + 1) + a;
}

/**
 * Main function.
 * @param argc the number of arguments
 * @param argv arguments
 * @return the return code
 */
int main(int argc, char *argv[]) {
    bool stop = FALSE, played;
    window_t *win_player, *win_computer, *win_infos;
    int n, rest, index;
    int posX, posY, x, y;
    unsigned char *player_grid, *computer_grid;
    int *player_rest, *computer_rest;
 
    // Initialize the pseudo-random number generator
    srand(time(NULL) + getpid());
 
    // #TODO# #1 create a shared memory segment that contains:
    // - the player and computer grids
    // - the boats counters
    // - the computer message to display
    
    // #TODO# #2 map the segment
    // - player_grid the player's grid
    // - computer_grid the computer's grid
    // - player_rest the number of player remaining boats
    // - computer_rest the number of computer remaining boats
    // - computer_msg the computer's message
    
    // #TODO# #3 to delete
    // Allocate the player grid
    if((player_grid = malloc(sizeof(unsigned char) * WIDTH * HEIGHT)) == NULL) {
        perror("Error allocate the player grid");
        exit(EXIT_FAILURE);
    }
    
    // #TODO# #4 to delete
    // Allocate the computer grid
    if((computer_grid = malloc(sizeof(unsigned char) * WIDTH * HEIGHT)) == NULL) {
        perror("Error allocate the computer grid");
        exit(EXIT_FAILURE);
    }
    
    // #TODO# #5 to delete
    // The counters are in the shared memory segment
    int tmp_joueur, tmp_ordi;
    player_rest = &tmp_joueur;
    computer_rest = &tmp_ordi;
    
    // Initialize the grids
    memset(player_grid, ' ', sizeof(unsigned char) * WIDTH * HEIGHT);
    memset(computer_grid, ' ', sizeof(unsigned char) * WIDTH * HEIGHT);
    
    // Intialize the remaining boats
    *player_rest = BOATS;
    *computer_rest = BOATS;
        
    // ncurses initialization
    ncurses_init();
    ncurses_init_mouse();
    ncurses_colors(); 
    palette();
    clear();
    refresh();
    
    // Check the terminal dimensions
    if((COLS < WIDTH * 2 + 2) || (LINES < HEIGHT + 9)) {
        ncurses_stop();
        fprintf(stderr, 
              "Dimensions are invalid (%d,%d). width must be greater than %d and height mut be greater than %d\n",
              COLS, LINES, WIDTH * 2 + 2, HEIGHT + 9);
        exit(EXIT_FAILURE);
    }
    
    // Create windows
    win_infos = window_create(0, 0, COLS, 7, "Informations", TRUE);
    win_player = window_create(0, 7, WIDTH + 2, HEIGHT + 2, "Player", FALSE);    
    win_computer = window_create(WIDTH + 2, 7, WIDTH + 2, HEIGHT + 2, "Computer", FALSE);    
    
    // Loop to place boats
    window_printw(win_infos, "Press 'S' to stop the game.");
    window_printw(win_infos, "\nPlace your %d boats by clicking in your grid.", BOATS);
    window_refresh(win_infos);
    rest = BOATS;
    while((stop == FALSE) && (rest > 0) && (n = getch())) {
        switch(n) {
            case 's':
            case 'S':
                stop = TRUE;
                break;
            case KEY_MOUSE:
                if(mouse_getpos(&posX, &posY) == OK) {
                    if(window_getcoordinates(win_player, posX, posY, &x, &y) == TRUE) {
                        if(player_grid[y * WIDTH + x] != 'X') {
                            player_grid[y * WIDTH + x] = 'X';
                            window_mvaddch_col(win_player, y, x, YELLOW, 'X');
                            window_refresh(win_player);
                            window_printw(win_infos, "\nYou place a boat at (%d,%d).", x, y);
                            rest--;
                        }
                        else
                            window_printw(win_infos, "\nThere's already a boat here...");
                        window_refresh(win_infos);
                    }
                }
                break;
        }
    }
    
    // Place computer boats
    if(stop == FALSE) {
        window_printw(win_infos, "\nWaiting for computer.");
        window_refresh(win_infos);
        
        // #TODO# #6 how to wait for the computer to start and place its boats?
        
        // #TODO# #7 to delete (code to be placed in computer.c)
        // Random fill
        rest = BOATS;
        while(rest > 0) {
            y = random_integer(0, HEIGHT - 1);
            x = random_integer(0, WIDTH - 1);
            
            index = y * WIDTH + x;
            if(computer_grid[index] == ' ') {
                computer_grid[index] = 'X';
                rest--;

                // Display the computer boats (you're a cheater!)
                window_mvaddch_col(win_computer, y, x, YELLOW, 'X');
                window_refresh(win_computer);
            }
        }
        
        window_printw(win_infos, "\nComputer is connected and has placed its boats.");
        window_refresh(win_infos);
    }    
    
    // Main loop
    while((stop == FALSE) && (*player_rest > 0) && (*computer_rest > 0)) {
        // Player's turn
        window_printw(win_infos, "\nClick in the computer grid to shot.");
        window_refresh(win_infos);
        played = FALSE;
        while((stop == FALSE) && (played == FALSE)) {
            n = getch();
            switch(n) {
                case 's':
                case 'S':
                    stop = TRUE;
                    break;
                case KEY_MOUSE:
                    if(mouse_getpos(&posX, &posY) == OK) {
                        if(window_getcoordinates(win_computer, posX, posY, &x, &y) == TRUE) {
                            index = y * WIDTH + x;
                            if((computer_grid[index] != ' ') && (computer_grid[index] != 'X'))
                                window_printw(win_infos, "\nYou already shoot here.");
                            else {
                                played = TRUE;
                                if(computer_grid[index] == 'X') {
                                    window_printw_col(win_infos, RED, "\nYou destroyed a boat.");
                                    window_mvaddch_col(win_computer, y, x, RED, 'X');
                                    window_refresh(win_computer);
                                    computer_grid[index] = 'T';
                                    *computer_rest -= 1;
                                }
                                else {
                                    window_printw(win_infos, "\nYou shot in water and you killed a dolphin.");
                                    window_mvaddch_col(win_computer, y, x, BLUE, 'M');
                                    window_refresh(win_computer);
                                    computer_grid[index] = 'M';
                                }
                            }
                            window_refresh(win_infos);
                        }
                    }
                    break;
            }
        }
        
        // Computer's turn
        if((stop == FALSE) && (*player_rest > 0) && (*computer_rest > 0)) {
            // #TODO# #8 how to wait for the computer to finish its turn?
            
            // #TODO# #9 to delete
            // Random choice of the computer
            do {
                y = random_integer(0, HEIGHT - 1);
                x = random_integer(0, WIDTH - 1);
            
                index = y * WIDTH + x;
            } while((player_grid[index] != ' ') && (player_grid[index] != 'X'));
            
            if(player_grid[index] == ' ') {
                player_grid[index] = 'M';
                window_mvaddch_col(win_player, y, x, BLUE, 'M');
            }
            else {
                player_grid[index] = 'T';
                *player_rest -= 1;
                window_mvaddch_col(win_player, y, x, RED, 'X');
            }
            window_refresh(win_player);
        
            // #TODO# #10
            // - Display the computer message in the shared memory segment
            // - Update the player grid (to display the computer shot)
        }
    }
    
    // End of the game or stop demanded
    if(stop == FALSE) {
        if(*player_rest == 0)
            window_printw_col(win_infos, RED, "\nYou lose!");
        else
            window_printw_col(win_infos, GREEN, "\nYou won!");
    }
    else
        window_printw(win_infos, "\nYou stoped the game.");
    window_refresh(win_infos);
    sleep(2);
    
    // Stop ncurses
    window_delete(&win_player);
    window_delete(&win_computer);
    window_delete(&win_infos);
    ncurses_stop();
    
    // #TODO# #11 to delete
    // Free memory
    free(player_grid);
    free(computer_grid);

    return EXIT_SUCCESS;    
}