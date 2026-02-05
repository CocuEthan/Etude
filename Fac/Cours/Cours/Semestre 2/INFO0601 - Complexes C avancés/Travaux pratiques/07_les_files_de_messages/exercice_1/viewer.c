#include <stdio.h>
#include <stdlib.h>
#include <ncurses.h>
#include <locale.h>
#include <sys/msg.h>
#include <sys/stat.h>
#include <string.h>
#include <unistd.h>

#include "functions.h"
#include "window.h"
#include "colors.h"
#include "include.h"

int main(int argc, char *argv[]) {
    bool stop = FALSE;
    // int msqid;
    window_t *win;
    // message_t msg;
    char buf[256];
    
    // ncurses initialization
    setlocale(LC_ALL, "");
    ncurses_init();
    ncurses_init_mouse();
    ncurses_colors(); 
    palette();
    clear();
    refresh();  
    
    // Check terminal size
    if((COLS < WIDTH) || (LINES < HEIGHT)) {
        ncurses_stop();
        fprintf(stderr, 
              "Dimensions are invalid (%d,%d). width must be greater than %d and height mut be greater than %d\n",
              COLS, LINES, WIDTH, HEIGHT);
        exit(EXIT_FAILURE);
    }
    
    // Create window to display messages
    win = window_create(0, 0, COLS, HEIGHT, "Messages", TRUE);
    
    // Create/get the message queue
    // #TODO#
    
    // Main lool
    while(stop == FALSE) {
        // Receive message
        // #TODO#
        
        // Stop or display message
        // #TODO# Modify "buf" by the correct field of your structure
        if(strcmp(buf, "#STOP#") == 0) {            
            stop = TRUE;
            window_printw(win, "Stop request received...\n");
            window_refresh(win);
            sleep(5);
        }
        else {
            window_printw(win, "%s\n", buf);
            window_refresh(win);
        }
    }
    
    // Stop ncurses
    window_delete(&win);
    ncurses_stop();

    // Delete queue
    // #TODO#
    printf("Queue deleted.\n");

    return EXIT_SUCCESS;    
}