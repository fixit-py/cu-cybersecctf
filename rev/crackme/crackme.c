#include <stdio.h>
#include <string.h>

int main() {
  char input[50];

  while (1) {
    printf("Enter the password: ");
    fflush(stdout);

    scanf("%49s", input);
    if (strcmp(input, "supeR_s3cr3t_p4ssw0rd") == 0)
      break;

    printf("Incorrect password! Try again.\n");
    fflush(stdout);
  }

  printf("Flag: CTF{B4d_P455worD_pr4ct1c3}\n");
  fflush(stdout);
  return 0;
}
