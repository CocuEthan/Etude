/**
 * This program illustrates the steganography by hiding a message in the
 * structure padding bytes and after the \0 character of a constant string.
 * It uses the low-level file functions.
 * Try: ./stegano -c example.bin
 *        => create example.bin
 *      ./stegano -d example.bin
 *        => display dummy events in example.bin
 *      ./stegano -h example.bin "It's a hidden message"
 *        => hide a message
 *      ./stegano -r example.bin
 *        => display the hidden message
 **/
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#define BUFFER_SIZE          1024
#define EVENTS_NB            100
#define MSG_SIZE             40

// Structure of an event
typedef struct {
  unsigned int code;         // Application code
  unsigned long date;        // Date
  int state;                 // Status 
  unsigned int priority;     // Event priority
  char message[MSG_SIZE];    // Message
} event_t;

/**
 * Display the hidden message in a file.
 * @param filename name of the events file
 */
void display(char *filename) {
    int fd;
    char buffer[BUFFER_SIZE];
    int i = 0, j, state = 0, stop = 0;
    event_t event;
    char *ptr;
    
    if((fd = open(filename, O_RDONLY)) == -1) {
        fprintf(stderr, "Error opening file '%s'", filename);
        perror("");
        exit(EXIT_FAILURE);
    }    
    memset(buffer, '?', sizeof(buffer));
    
    // Read the first event
    if(read(fd, &event, sizeof(event)) == -1) {
        perror("Error reading event (1)");
        exit(EXIT_FAILURE);
    }
    ptr = (char*)&event.code;
    j = 4;
    while(stop == 0) {
        // Get next character
        buffer[i] = ptr[j];
        j++;
        i++;
        
        // Detect message end
        if(buffer[i] == '\0')
            stop = 1;
        else {
            if(state == 0) {
                if(j == 8) {
                    j = strlen(event.message) + 1;
                    ptr = event.message;
                    state = 1;
                }
            }
            else { // State = 1
                if(j == MSG_SIZE) {
                    // Read next event
                    if(read(fd, &event, sizeof(event)) == -1) {
                        perror("Error reading event (2)");
                        exit(EXIT_FAILURE);
                    }
                    ptr = (char*)&event.code;
                    j = 4;
                    state = 0;
                }
            }
        }
    }
    
    printf("Message read: '%s'\n", buffer);
    
    // Close file
    if(close(fd) == -1) {
        perror("Error closing file");
        exit(EXIT_FAILURE);
    }    
}

/**
 * Hide a message in a file.
 * @param filename name of the events file
 * @param message the message to hide
 */
void hide(char *filename, char *message) {
    int fd;
    int i = 0, j, state = 0, stop = 0;
    event_t event;
    char *ptr;
    size_t size = strlen(message) + 1;
    
    // Open file
    if((fd = open(filename, O_RDWR)) == -1) {
        fprintf(stderr, "Error opening file '%s'", filename);
        perror("");
        exit(EXIT_FAILURE);
    }

    // Read the first event
    if(read(fd, &event, sizeof(event)) == -1) {
        perror("Error reading event (1)");
        exit(EXIT_FAILURE);
    }
    
    // Position pointer on code field
    ptr = (char*)&event.code;
    j = 4;
    
    while(stop == 0) {
        // Set next character
        printf("Hide '%c' (#%d) ; state=%d ; pos=%d\n", message[i], i, state, j);
        ptr[j] = message[i];
        j++;
        i++;
        
        // Detect message end
        if(i == size)
            stop = 1;
        else {
            if(state == 0) {
                if(j == 8) {
                    j = strlen(event.message) + 1;
                    ptr = event.message;
                    state = 1;
                }
            }
            else { // State = 1
                if(j == MSG_SIZE) {
                    // Move back
                    if(lseek(fd, -sizeof(event), SEEK_CUR) == -1) {
                        perror("Error positioning in file");
                        exit(EXIT_FAILURE);
                    }
                    
                    // Write modified event
                    if(write(fd, &event, sizeof(event)) == -1) {
                        perror("Error writing event in file");
                        exit(EXIT_FAILURE);
                    }
                    
                    // Read next event
                    if(read(fd, &event, sizeof(event)) == -1) {
                        perror("Error reading event (2)");
                        exit(EXIT_FAILURE);
                    }
                    ptr = (char*)&event.code;
                    j = 4;
                    state = 0;
                }
            }
        }
    }
    
    // Move back
    if(lseek(fd, -sizeof(event), SEEK_CUR) == -1) {
        perror("Error positioning in file");
        exit(EXIT_FAILURE);
    }
    
    // Write last modified event
    if(write(fd, &event, sizeof(event)) == -1) {
        perror("Error writing event in file");
        exit(EXIT_FAILURE);
    }
    
    printf("The message was hidden.\n");
    
    // Close file
    if(close(fd) == -1) {
        perror("Error closing file");
        exit(EXIT_FAILURE);
    }
}

int main(int argc, char *argv[]) {
    event_t event;
    int i, fd;
    
    // Check arguments
    if((argc != 3) && (argc != 4)) {
        fprintf(stderr, "Create an events file  : %s -c file.bin where 'file.bin' is the file to create.\n", argv[0]);
        fprintf(stderr, "Display a file         : %s -d file.bin where 'file.bin' is the file to display.\n", argv[0]);
        fprintf(stderr, "Read the hidden message: %s -r file.bin where 'file.bin' is the file containing the message.\n", argv[0]);
        fprintf(stderr, "Hide a message         : %s -h file.bin m where 'file.bin' is the destination file and 'm' the message.\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    if(argc == 3) {
        if(strcmp(argv[1], "-c") == 0) {
            // Create file
            if((fd = open(argv[2], O_CREAT | O_TRUNC | O_WRONLY, S_IRUSR | S_IWUSR)) == -1) {
                fprintf(stderr, "Error creating file '%s'", argv[2]);
                perror("");
                exit(EXIT_FAILURE);
            }
            
            // Write dummy events
            for(i = 0; i < EVENTS_NB; i++) {
                event.code = i;
                event.date = i;
                event.state = i;
                event.priority = i;
                snprintf(event.message, MSG_SIZE, "Message of event #%d", i);
                
                if(write(fd, &event, sizeof(event_t)) == -1) {
                    fprintf(stderr, "Error writing event #%i", i);
                    perror("");
                    exit(EXIT_FAILURE);
                }
            }
            
            // Close file
            if(close(fd) == -1) {
                perror("Error closing file");
                exit(EXIT_FAILURE);
            }
        }
        else if(strcmp(argv[1], "-d") == 0) {
            // Display file content
            if((fd = open(argv[2], O_RDONLY)) == -1) {
                fprintf(stderr, "Erreur lors de l'ouverture du fichier '%s'\n", argv[2]);
                perror("");
                exit(EXIT_FAILURE);
            }
            
            // Read dummy events
            while((i = read(fd, &event, sizeof(event_t))) > 0) {
                printf("%d %ld %d %d %s\n", event.code, event.date, event.state, event.priority, event.message);
            }
            if(i == -1) {
                perror("Error reading event");
                exit(EXIT_FAILURE);
            }
            
            // Close file
            if(close(fd) == -1) {
                perror("Error closing file");
                exit(EXIT_FAILURE);
            }
        }
        else if(strcmp(argv[1], "-r") == 0) {
            // Display hidden message
            display(argv[2]);
        }
        else {
            fprintf(stderr, "Incorrect option.\n");
            exit(EXIT_FAILURE);
        }
    }
    else {
        if(strcmp(argv[1], "-h") == 0) {
            // Hide a message
            if(strlen(argv[3]) + 1 >= MSG_SIZE) {
                fprintf(stderr, "The message must not exceed %d characters.\n", MSG_SIZE);
                exit(EXIT_FAILURE);
            }
            
            hide(argv[2], argv[3]);
        }
        else {
            fprintf(stderr, "Incorrect option.\n");
            exit(EXIT_FAILURE);
        }
    }
    
    return EXIT_SUCCESS;
}