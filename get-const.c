#include <linux/fs.h>
#include <stdio.h>

int main(int argc, char* argv[]) {
    printf("FIBMAP: %x\nFIGETBSZ: %x\n", FIBMAP, FIGETBSZ);
    return 0;
}
