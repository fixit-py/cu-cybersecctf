#include <stdio.h>

int main() {
  int input;

  while (1) {
    printf("Enter a number: ");
    fflush(stdout);

    if (scanf("%d", &input) != 1) {
      printf("Invalid input.\n");
      fflush(stdout);
      return 1;
    }

    long result = ((input * 2) + 10) * 3;

    if (result == 557155098)
      break;

    printf("Try harder!\n");
    fflush(stdout);
  }

  printf("Flag: CTF{Y0U_AR3_th3_m4th_m4st3r}");
  fflush(stdout);
  return 0;
}
