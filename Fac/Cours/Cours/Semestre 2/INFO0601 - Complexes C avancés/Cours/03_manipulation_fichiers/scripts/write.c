/**
 * Asks the user for an integer and writes it to the file 'toto.bin'.
 * It uses system calls 'open', 'write' and 'close'.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
 
int main(int argc, char* argv[]) {
  int fd, i;
      
  // Asks the user an integer
  printf("Enter an integer: ");
  if(scanf("%d", &i) != 1) {
    fprintf(stderr, "Incorrect entry.\n");
    exit(EXIT_FAILURE);
  }
  
  // Create file
  if((fd = open("toto.bin", O_WRONLY|O_CREAT, S_IRUSR|S_IWUSR)) == -1) {
    perror("Error opening file");
    exit(EXIT_FAILURE);
  }    
  
  // Write the integer
  if(write(fd, &i, sizeof(int)) == -1) {
    perror("Error writing the integer");
    exit(EXIT_FAILURE);
  }
  printf("Integer written in file\n");
  
  // Close file
  if(close(fd) == -1) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}