#include <stdio.h>

int security_code = 0x21646f63; // "cod!" in little endian

int main() {
    char transmission[1024];
    char classified_data[64];
    
    printf("=== ORBITAL STATION ALPHA-7 SECURE TERMINAL ===\n");
    printf("Security protocols are active. Authorization required.\n");
    printf("Only personnel with proper clearance codes can access classified files.\n");
    printf("Enter your transmission: ");
    fflush(stdout);
    
    scanf("%1024s", transmission);
    
    printf("Transmission received: ");
    printf(transmission);
    printf("\n");
    fflush(stdout);
    
    if (security_code == 0x64657461) { // "ated" in little endian (creates "codeated" -> "authenticated")
        printf("AUTHENTICATION SUCCESSFUL - Welcome, authorized personnel!\n");
        printf("Accessing classified orbital research data...\n\n");
        
        // Read classified data
        FILE *classified_file = fopen("flag.txt", "r");
        if (classified_file != NULL) {
            fgets(classified_data, 64, classified_file);
            printf("CLASSIFIED DATA: %s", classified_data);
            fclose(classified_file);
        } else {
            printf("ERROR: Classified data file not found\n");
        }
        fflush(stdout);
    }
    else {
        printf("AUTHENTICATION FAILED\n");
        printf("Current security code: 0x%x\n", security_code);
        printf("Access denied. Please verify your credentials.\n");
        fflush(stdout);
    }
    
    return 0;
}
