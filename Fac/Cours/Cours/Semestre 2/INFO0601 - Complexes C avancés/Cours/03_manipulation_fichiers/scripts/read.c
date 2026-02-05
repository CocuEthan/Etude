/**
 * Reads an integer from the file 'toto.bin' and displays it.
 * It uses system calls 'open', 'read' and 'close'.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
 
int main(int argc, char* argv[]) {
  int fd, i, n;
  
  // Create file
  if((fd = open("toto.bin", O_RDONLY)) == -1) {
    perror("Error opening file");
    exit(EXIT_FAILURE);
  }    
  
  // Read integer
  if((n = read(fd, &i, sizeof(int))) == -1) {
    perror("Error reading integer");
    exit(EXIT_FAILURE);
  }
  
  if(n == 0)
      printf("No integer to read.\n");
  else
    printf("Integer read: %d\n", i);
  
  // Close file
  if(close(fd) == -1) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}