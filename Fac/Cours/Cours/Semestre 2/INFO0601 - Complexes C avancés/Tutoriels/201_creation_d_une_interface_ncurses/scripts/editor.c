/**
 * This program is a graphic editor. Its purpose is to illustrate a
 * creation of an interface with ncurses library.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <locale.h>
#include <unistd.h>

#include "functions.h"
#include "window.h"
#include "image.h"
#include "interface.h"
#include "colors.h"

int main(int argc, char *argv[]) {
    int ch;
    unsigned short width, height;
    interface_t *interface;
    image_t *image;
    bool quit = FALSE;

    // Check arguments    
    if(argc == 2) {
        // Load a file
        if((image = image_load(argv[1])) == NULL) {
            fprintf(stderr, "File '%s' does'nt exist.\n", argv[1]);
            exit(EXIT_FAILURE);
        }
    }
    else if(argc == 4) {
        // Create new file
        if(access(argv[1], F_OK) == 0) {
            fprintf(stderr, "File '%s' already exists.\n", argv[1]);
            exit(EXIT_FAILURE);
        }
        
        width = atoi(argv[2]);
        height = atoi(argv[3]);
        
        if((width < 10) || (width > 80) || (height < 10) || (height > 20)) {
            fprintf(stderr, "Dimensions are invalid (%d,%d). width must be between 10 and 80, height between 10 and 20\n", width, height);
            exit(EXIT_FAILURE);
        }
        
        image = image_create(width, height);
    }
    else {
        // Bad arguments
        fprintf(stderr, "Load a file:\n\t%s file\n\t\tfile: file to load\n", argv[0]);
        fprintf(stderr, "Create a new file:\n\t%s file width height\n\t\tfile: file to create\n", argv[0]);
        fprintf(stderr, "\t\twidth: width of the image\n");
        fprintf(stderr, "\t\theight: height of the image\n");
        exit(EXIT_FAILURE);
    }

    // ncurses initialisation
    setlocale(LC_ALL, "");
    ncurses_init();
    ncurses_init_mouse();
    ncurses_colors(); 
    palette();
    clear();
    refresh();  

    // Create interface
    interface = interface_create(image);

    // Main loop
    while(quit == FALSE) {
        ch = getch();
        if((ch == 'Q') || (ch == 'q'))
          quit = true;
        else
          interface_actions(interface, ch);
    }
    
    // Stop ncurses
    ncurses_stop();
    
    // Save the image
    image_save(argv[1], image);

    // Delete interface
    interface_delete(&interface);

    return EXIT_SUCCESS;
}