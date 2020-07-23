  program a
  integer, parameter :: n=10000
  integer i,nb

  nb = 4
!tune$ param define NB type int range 2,4,8 
!tune$ param define mode type label range "sym","non sym" default sym
!tune$ inject_r:  nb = NB
  do i=1,n,nb
   do ii=i,i+nb-1
    print *,ii
   end do
  end do

!tune$ begin replace
  print *,mode
!tune$ end replace
  end
