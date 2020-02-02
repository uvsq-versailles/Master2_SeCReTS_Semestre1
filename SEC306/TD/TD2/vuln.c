#include <stdio.h>
#define TAILLE_MAXIMUM_PRENOM 64

void ask_me_im_famous()
{
    char prenom[TAILLE_MAXIMUM_PRENOM];
    gets(prenom);
}

int main(int argc, char** argv, char** envp)
{
    puts("Tapez votre prénom :");
    ask_me_im_famous();
    puts("Bonjour !");

    return 0;
}

