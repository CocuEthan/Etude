#include <stdlib.h>

#include "window.h"
#include "functions.h"
#include "image.h"
#include "colors.h"

#include "interface.h"

/**
 * Check terminal dimensions.
 * @param[in] width image width
 * @param[out] height image height
 */
void interface_dimensions(unsigned short width, unsigned short height) {
    if((COLS < width + 17) || (LINES < height + 12)) {
        ncurses_stop();
        fprintf(stderr, 
              "Terminal size is too small: actually w=%d,h=%d instead of l=%d,h=%d\n",
              COLS, LINES, width + 17, height + 12);
        exit(EXIT_FAILURE);
    } 
}

/**
 * Create interface.
 * @param[in] image the image
 * @return created interface
 */
interface_t *interface_create(image_t *image) {
    interface_t *result;
    int i;
    
    // Check terminal dimensions
    interface_dimensions(image->width, image->height);
    
    // Structure allocation
    if((result = malloc(sizeof(interface_t))) == NULL) {
        ncurses_stop();
        perror("Error allocating structure");
        exit(EXIT_FAILURE);
    }
    result->image = image;
    
    // Create information window
    result->win_infos = window_create(0, 0, COLS, 10, "Informations", TRUE);
    window_printw_col(result->win_infos, RED, "Press 'Q' to quit");
    window_printw(result->win_infos, "\nClick on a color and click on the image... that's all!");
    window_refresh(result->win_infos);

    // Create palette window
    result->win_palette = window_create(image->width + 2, 10, 15, 10, "Palette", FALSE);
    result->selection = BK_WHITE;
    interface_palette_update(result);

    // Create image window
    result->win_image = window_create(0, 10, 2 + image->width, 2 + image->height, "Image", FALSE);
    for(i = 0; i < image->height * image->width; i++) {
        window_addch_col(result->win_image, image->image[i], ' ');
    }
    window_refresh(result->win_image);

    return result;
}

/**
 * Delete interface.
 * @param[in,out] interface the interface to delete
 */
void interface_delete(interface_t **interface) {
    window_delete(&(*interface)->win_infos);
    window_delete(&(*interface)->win_palette);
    window_delete(&(*interface)->win_image);
    image_delete(&(*interface)->image);
    free(*interface);
    interface = NULL;
}

/**
 * Update palette window
 * @param[in,out] interface the interface
 */
void interface_palette_update(interface_t *interface) {
    struct {
        color_t color;
        char *title;
    } t[8] = {
        { .color = WHITE, .title = "Black" },
        { .color = BK_WHITE, .title = "White" },
        { .color = BK_GREEN, .title = "Green" },
        { .color = BK_BLUE, .title = "Blue" },
        { .color = BK_RED, .title = "Red" },
        { .color = BK_YELLOW, .title = "Yellow" },
        { .color = BK_CYAN, .title = "Cyan" },
        { .color = BK_MAGENTA, .title = "Magenta" },
    };
    
    window_erase(interface->win_palette);
    
    for(int i = 0; i < 8; i++) {    
        window_printw_col(interface->win_palette, WHITE, " ");
        if(interface->selection == t[i].color) {
            window_color(interface->win_palette, WHITE);
            window_printw(interface->win_palette, "X %s\n", t[i].title);
        }
        else {
            window_color(interface->win_palette, RED);
            window_printw(interface->win_palette, "  %s\n", t[i].title);
        }
    }

    window_refresh(interface->win_palette);
}

/**
 * Manage actions in the palette window.
 * @param[in,out] interface the interface
 * @param[in] posX X position of the click in the window
 * @param[in] posY Y position of the click in the window
 */
void interface_palette_actions(interface_t *interface, int posX, int posY) {
    struct {
        color_t color;
        char *title;
    } t[8] = {
        { .color = WHITE, .title = "Black" },
        { .color = BK_WHITE, .title = "White" },
        { .color = BK_GREEN, .title = "Green" },
        { .color = BK_BLUE, .title = "Blue" },
        { .color = BK_RED, .title = "Red" },
        { .color = BK_YELLOW, .title = "Yellow" },
        { .color = BK_CYAN, .title = "Cyan" },
        { .color = BK_MAGENTA, .title = "Magenta" },
    };
    
    if((posY >= 0) && (posY <= 7)) {
        interface->selection = t[posY].color;
        interface_palette_update(interface);
    }
}

/**
 * Manage actions in the image window.
 * @param[in,out] interface l'interface
 * @param[in] posX X position of the click in the window
 * @param[in] posY Y position of the click in the window
 */
void interface_image_actions(interface_t *interface, int posX, int posY) {
    interface->image->image[posY * interface->image->width + posX] = interface->selection;
    window_mvaddch_col(interface->win_image, posY, posX, interface->selection, ' ');
    window_refresh(interface->win_image);
}

/**
 * Manage actions of the user.
 * @param[in,out] interface the interface
 * @param[in] c the pressed key
 */
void interface_actions(interface_t *interface, int c) {
    int mouseX, mouseY, posX, posY;

    // Mouse management
    if((c == KEY_MOUSE) && (mouse_getpos(&mouseX, &mouseY) == OK)) {
#ifdef _DEBUG_
        window_printw(interface->win_infos, "\nClick (%d,%d)", mouseX, mouseY);
        window_refresh(interface->win_infos);
#endif
        
        if(window_getcoordinates(interface->win_palette, mouseX, mouseY, &posX, &posY)) {
            interface_palette_actions(interface, posX, posY);
        }
        else if(window_getcoordinates(interface->win_image, mouseX, mouseY, &posX, &posY)) {
            interface_image_actions(interface, posX, posY);
        }
    }
    else {
        /* Key management: to modify for the project */
        if((c >= '0') && (c <= '8'))
            interface_palette_actions(interface, 0, c - '0');
        else
            switch(c) {
                default:
#ifdef _DEBUG_                
                    window_printw(interface->win_infos, "\nKey %d pressed", c);
                    window_refresh(interface->win_infos);
#endif
                    break;
            }
    }
}