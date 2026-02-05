/**
 * It writes 5 integers in a file and displays the size of the file. Then,
 * the file is truncated with system call 'ftruncate'. Finaly, the program
 * displays the new size of the file.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
 
int main(int argc, char* argv[]) {
  int fd, i;
  off_t pos;
  
  // Create file
  if((fd = open("toto.bin", O_RDWR|O_CREAT|O_TRUNC, S_IRUSR|S_IWUSR)) == -1) {
    perror("Error opening file");
    exit(EXIT_FAILURE);
  }
  
  // Write 5 integers
  for(i = 0; i < 5; i++) {
    if(write(fd, &i, sizeof(int)) == -1) {
      perror("Error writing integer");
      exit(EXIT_FAILURE);
    }
  }
  
  // Reposition the offset at the end of the file and get the new position
  if((pos = lseek(fd, 0, SEEK_END)) == -1) {
    perror("Error repositioning offset");
    exit(EXIT_FAILURE);
  }
  printf("Size before truncate: %ld\n", pos);
  
  // Truncate the file
  if(ftruncate(fd, sizeof(int) * 2) == -1) {
    perror("Error truncating");
    exit(EXIT_FAILURE);
  }
  
  // Reposition the offset at the end of the file and get the new position
  if((pos = lseek(fd, 0, SEEK_END)) == -1) {
    perror("Error repositioning offset");
    exit(EXIT_FAILURE);
  }
  printf("Size after truncate: %ld\n", pos);
  
  // Close file
  if(close(fd) == -1) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  
  return EXIT_SUCCESS;
}