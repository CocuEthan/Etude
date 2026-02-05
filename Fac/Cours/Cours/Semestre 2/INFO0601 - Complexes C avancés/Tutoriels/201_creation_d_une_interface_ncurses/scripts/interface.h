#ifndef _INTERFACE_
#define _INTERFACE_

// Structure for the application interface
typedef struct {
    window_t *win_infos;     // Informations window
    window_t *win_palette;   // Palette window
    window_t *win_image;     // Image window
    image_t *image;          // The image
    unsigned int selection;  // Selected color
} interface_t;

/**
 * Check terminal dimensions.
 * @param[in] width image width
 * @param[out] height image height
 */
void interface_dimensions(unsigned short width, unsigned short height);

/**
 * Create interface.
 * @param[in] image the image
 * @return created interface
 */
interface_t *interface_create(image_t *image);

/**
 * Delete interface.
 * @param[in,out] interface the interface to delete
 */
void interface_delete(interface_t **interface);

/**
 * Update palette window
 * @param[in,out] interface the interface
 */
void interface_palette_update(interface_t *interface);

/**
 * Manage actions in the palette window.
 * @param[in,out] interface the interface
 * @param[in] posX X position of the click in the window
 * @param[in] posY Y position of the click in the window
 */
void interface_palette_actions(interface_t *interface, int posX, int posY);

/**
 * Manage actions in the image window.
 * @param[in,out] interface l'interface
 * @param[in] posX X position of the click in the window
 * @param[in] posY Y position of the click in the window
 */
void interface_image_actions(interface_t *interface, int posX, int posY);

/**
 * Manage actions of the user.
 * @param[in,out] interface the interface
 * @param[in] c the pressed key
 */
void interface_actions(interface_t *interface, int c);

#endif