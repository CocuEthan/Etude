/**
 * This program deletes a message queue whose key has passed as an argument.
 * @author Cyril Rabat
 **/
#include <stdlib.h>
#include <stdio.h>
#include <sys/msg.h>

int main(int argc, char *argv[]) {
    int msqid;
    key_t key;

    // Check the arguments
    if(argc != 2) {
        fprintf(stderr, "You must specify the key of the message queue as argument.\n");
        exit(EXIT_FAILURE);
    }
    key = (key_t)atoi(argv[1]);

    // Get the message queue
    if((msqid = msgget(key, 0)) == -1) {
        perror("Error getting the message queue identifier");
        exit(EXIT_FAILURE);
    }

    // Delete the message queue
    if(msgctl(msqid, IPC_RMID, 0) == -1) {
        perror("Error deleting message queue");
        exit(EXIT_FAILURE);
    }
    printf("Message queue deleted.\n");

    return EXIT_SUCCESS;
}