#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/msg.h>
#include <ncurses.h>

#include "include.h"

#define xstr(s) str(s)
#define str(s) #s

int main(int argc, char *argv[]) {
    // int msqid;
    // message_t msg;
    bool stop = FALSE;
    char c;
    char buf[256];
    
    // Get the message queue
    // #TODO#
    
    // Main loop
    printf("Type messages; #QUIT# to quit, #STOP# to stop the viewer\n");
    while(stop == FALSE) {
        printf("Type a message: ");
        if(scanf("%"xstr(MAX_MSG)"[^\n]", buf) != 1) {
            fprintf(stderr, "Nothing to read\n");
            exit(EXIT_FAILURE);
        }
        while(((c = getchar()) != '\n') || (c == EOF));
        
        // #TODO# Modify "buf" by the correct field of your structure
        if(strcmp(buf, "#QUIT#") == 0)
            stop = TRUE;
        else {
            // Send the message
            // #TODO#
            printf("Message sent.\n");
            
            if(strcmp(buf, "#STOP#") == 0)
                stop = TRUE;
        }
    }
    
    return EXIT_SUCCESS;
}