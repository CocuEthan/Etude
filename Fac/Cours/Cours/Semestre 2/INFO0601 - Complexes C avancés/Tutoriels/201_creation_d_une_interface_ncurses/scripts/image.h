#ifndef _IMAGE_
#define _IMAGE_

// Image structure
typedef struct {
    unsigned short width;          // Image width
    unsigned short height;         // Image height
    unsigned char *image;          // Matrix
} image_t;

/**
 * Create a new image.
 * @param[in] width image width
 * @param[in] height image height
 * @return new image
 */
image_t *image_create(unsigned short width, unsigned short height);

/**
 * Delete an image.
 * @param[in,out] image image to delete
 */
void image_delete(image_t **image);

/**
 * Save the image in a binary file.
 * @param[in] filename name of the file
 * @param[in] image image to save
 */
void image_save(char *filename, image_t *image);

/**
 * Load an image from a file.
 * @param[in] filename name of the file
 * @return the loaded image or NULL on error
 */
image_t *image_load(char *filename);

#endif