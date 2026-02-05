/**
 * Writes an integer and a string to the file 'toto.bin'.
 * It uses 'fopen', 'fwrite' and 'fclose'.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
 
int main(int argc, char* argv[]) {
  FILE *f;                   // Stream
  char *buffer = "Hello";    // String to write
  int value = 65;            // Integer to write

  // Open file
  if((f = fopen("toto.bin", "w")) == NULL) {
    perror("Error opening file");
    exit(EXIT_FAILURE);
  }
  
  // Write the integer and the string
  if(fwrite(&value, sizeof(int), 1, f) == 0) {
    perror("Error writing integer");
    exit(EXIT_FAILURE);
  }
  printf("Integer written\n");
  if(fwrite(buffer, sizeof(char), 5, f) < 5) {
    perror("Error writing string");
    exit(EXIT_FAILURE);
  }
  printf("String written\n");
  
  // Close file
  if(fclose(f) == EOF) {
    perror("Error closing file");
    exit(EXIT_FAILURE);
  }
  printf("You can now read the file\n");
  
  return EXIT_SUCCESS;
}