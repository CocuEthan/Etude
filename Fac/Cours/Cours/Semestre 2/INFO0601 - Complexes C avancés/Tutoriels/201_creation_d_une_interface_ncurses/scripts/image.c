#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

#include "image.h"
#include "window.h"
#include "interface.h"
#include "functions.h"
#include "colors.h"

/**
 * Create a new image.
 * @param[in] width image width
 * @param[in] height image height
 * @return new image
 */
image_t *image_create(unsigned short width, unsigned short height) {
    image_t *result;
    
    if((result = malloc(sizeof(image_t))) == NULL) {
        ncurses_stop();
        perror("Error creating image");
        exit(EXIT_FAILURE);
    }
    
    if((result->image = malloc(sizeof(char) * width * height)) == NULL) {
        ncurses_stop();
        perror("Error allocating image");
        exit(EXIT_FAILURE);
    }
    memset(result->image, WHITE, width * height * sizeof(char));
    
    result->width = width;
    result->height = height;
    
    return result;
}

/**
 * Delete an image.
 * @param[in,out] image image to delete
 */
void image_delete(image_t **image) {
    free((*image)->image);
    free(*image);
    *image = NULL;
}

/**
 * Save the image in a binary file.
 * @param[in] filename name of the file
 * @param[in] image image to save
 */
void image_save(char *filename, image_t *image) {
    int fd;
    
    if((fd = open(filename, O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR |S_IWUSR)) == -1) {
        fprintf(stderr, "Erreur opening file '%s'", filename);
        perror("");
        exit(EXIT_FAILURE);
    }
    
    if(write(fd, &(image->width), sizeof(unsigned short)) == -1) {
        perror("Error writting width");
        exit(EXIT_FAILURE);
    }
    
    if(write(fd, &(image->height), sizeof(unsigned short)) == -1) {
        perror("Error writting height");
        exit(EXIT_FAILURE);        
    }
    
    if(write(fd, image->image, sizeof(unsigned char) * image->width * image->height) == -1) {
        perror("Error writting matrix");
        exit(EXIT_FAILURE);        
    }
    
    if(close(fd) == -1) {
        perror("Error closing file");
        exit(EXIT_FAILURE);
    }
}

/**
 * Load an image from a file.
 * @param[in] filename name of the file
 * @return the loaded image or NULL on error
 */
image_t *image_load(char *filename) {
    image_t *result = NULL;
    int fd;
        
    if((fd = open(filename, O_RDONLY)) == -1) {
        if(errno != ENOENT) {
            fprintf(stderr, "Error opening file '%s'", filename);
            perror("");
            exit(EXIT_FAILURE);
        }
    }
    
    if(fd != -1) {
        if((result = malloc(sizeof(image_t))) == NULL) {
            perror("Error allocating image");
            exit(EXIT_FAILURE);
        }
        
        if(read(fd, &(result->width), sizeof(unsigned short)) == -1) {
            perror("Error reading width");
            exit(EXIT_FAILURE);
        }
        
        if(read(fd, &(result->height), sizeof(unsigned short)) == -1) {
            perror("Error reading height");
            exit(EXIT_FAILURE);
        }
        
        if((result->image = malloc(sizeof(char) * result->width * result->height)) == NULL) {
            perror("Error allocating matrix");
            exit(EXIT_FAILURE);
        }
        
        if(read(fd, result->image, sizeof(unsigned char) * result->width * result->height) == -1) {
            perror("Error reading matrix");
            exit(EXIT_FAILURE);
        }
        
        if(close(fd) == -1) {
            perror("Error closing file");
            exit(EXIT_FAILURE);
        }    
    }
    
    return result;
}