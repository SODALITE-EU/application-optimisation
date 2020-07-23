#include <stdio.h>

void sub(){

  int n,i,ii,nb;
  double a;

#pragma tune param import NB
#pragma tune inject_r$:  nb=$NB;
  for(i=1;i<n;i+=nb) 
   for(ii=i;ii<i+nb;ii++) printf("%d",n);

#pragma tune begin replace
  subsub(a,NB);
  printf("NB = %d",NB);
#pragma tune end replace
  printf("end NB");

}


