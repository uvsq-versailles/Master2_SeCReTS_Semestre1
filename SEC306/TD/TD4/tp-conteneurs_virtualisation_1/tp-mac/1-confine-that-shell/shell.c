#include <unistd.h>     /* setuid, .. */
#include <sys/types.h>  /* setuid, .. */
#include <grp.h>        /* setgroups */
#include <stdio.h>      /* perror */

int main (int argc, char** argv) {

  gid_t newGrp = 0;

  /**
   *     if you installed programming manual pages, you can get the
   *         man page for execve 'man execvp'. Same goes for all the
   *             other system calls that we're using here.
   *                */

  /* this will tattoo the suid bit so that bash won't see that
   *      we're not really root. we also drop all other memberships
   *           just in case we're running with PAGs (in AFS)
   */
  if (setuid(0) != 0) {
    perror("Setuid failed, no suid-bit set?");
    return 1;
  }
  setgid(0);
  seteuid(0);
  setegid(0);
  /* we also drop all the groups that the old user had
   *      (verify with id -tool afterwards)
   *           this is not strictly necessary but we want to get rid of the
   *                groups that the original user was part of.
   */
  setgroups(1, &newGrp);

  /* load the default shell on top of this program
   *      to exit from the shell, use 'exit' :-)
   */
  execvp("/bin/sh", argv);
  return 0;
}
