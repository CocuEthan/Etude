# Scripts of course #4

## Compilation

To compile, type the following command:

```bash
make
```

** Warning ** For a reason exposed in the course, the gcc option `O3` has been deleted in `makefile`. Do use this makefile in your projects or add this option in the variable `CCFLAGS_STD`.

## Programs/files

Here is the list of the generated programs or files used:
- `pointers`: use of generic pointers with `read` and `write`
- `sizes`: size of variables (`int`, `double` and static array)
- `scanf1`: buffer overflow example with `scanf`
- `scanf2`: read 2 strings with `scanf`
- `fgets`: example of using `fgets`
- `initializations`: initializations of a static and a dynamic strings
- `stringstorage1`: write a static string into a binary file and read it
- `stringstorage2`: write a static string into a binary file and read it character by character.
- `stringstorage3`: stockage d'une chaîne de caractères de longueur variable dans un fichier en sauvegardant la taille puis la chaîne
- `structures1`: passing a structure as a parameter
- `structures2`: passing a structure with dynamic fields as a parameter
- `structuresize1`: size of structures
- `structurestorage1`: store a structure with static fields
- `structuresize2`: size of structures (to illustrate memory alignment)
- `structurestorage2`: store a structure with dynamic fields (warning, do not use!!!)
- `structurestorage3`: store a structure with dynamic fields (with the good method)
- `speed1.c`: comparison of speed according to the type of parameter passing
- `speed2.c`: comparison of speed between static or dynamic declaration
