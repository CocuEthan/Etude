/**
 * Program illustrating how msgget works to create a private message queue.
 * Warning: this program create a new file at each execution. Delete them with
 * ipcrm -q X where X is the message queue identifier.
 * @author Cyril Rabat
 */
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <sys/msg.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    int msqid;
  
    // Create the private message queue
    if((msqid = msgget(IPC_PRIVATE, S_IRUSR | S_IWUSR | IPC_CREAT | IPC_EXCL)) == -1) {
        perror("Error creating the file");
        exit(EXIT_FAILURE);
    }
    printf("Message queue (id=%d) created successfully...\n", msqid);
    printf("Type: `ipcrm -q %d` to delete it.\n", msqid);

    return EXIT_SUCCESS;
}