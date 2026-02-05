/**
 * This program recursively lists a directory.
 * @author Cyril Rabat
 **/
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>

/**
 * List a directory.
 * @param path the path of the directory
 */
void list_directory(char *path) {
  DIR *dirp;            // Directory
  struct dirent *dp;    // Directory entry
  struct stat s;        // File statistics
  char buf[256];        // Buffer

  // Open directory
  printf("**** Directory '%s'\n", path);
  if((dirp = opendir(path)) == NULL) {
    fprintf(stderr, "Error open '%s'.\n", path);
    exit(EXIT_FAILURE);
  }

  // Display directory content
  while((dp = readdir(dirp)) != NULL)
    if((strcmp(dp->d_name, ".") != 0) && (strcmp(dp->d_name, "..") != 0))
      printf("%s\n", dp->d_name);
  printf("\n");
  
  // Recursive calls for subdirectories
  rewinddir(dirp);
  while((dp = readdir(dirp)) != NULL) {
    if(snprintf(buf, 256, "%s/%s", path, dp->d_name) < 0) {
      fprintf(stderr, "Path too long: %s/%s.\n", path, dp->d_name);
      exit(EXIT_FAILURE);
    }
    
    if(stat(buf, &s) == -1) {
      fprintf(stderr, "Error stat on '%s'.\n", buf);
      exit(EXIT_FAILURE);
    }
    if((strcmp(dp->d_name, ".") != 0) && 
       (strcmp(dp->d_name, "..") != 0) &&
       (S_ISDIR(s.st_mode)))	  
      list_directory(buf);
  }

  // Close directory
  if(closedir(dirp) == -1) {
    perror("Error closing directory");
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char **argv) {
  if(argc != 2) {
    fprintf(stderr, "Use: %s dir\n\tWhere\n\t\tdir: directory to list\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  
  list_directory(argv[1]);
  
  return EXIT_SUCCESS;
}