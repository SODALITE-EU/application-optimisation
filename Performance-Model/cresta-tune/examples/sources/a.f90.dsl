  program a
  integer, parameter :: n=10000
  integer i,nb

!tune$ begin skip
! commment 1
! comment 2
!tune$ end skip

  nb = 4
!tune$ param import NB
!tune$ inject_r:  nb = NB
  do i=1,n,nb
   do ii=i,i+nb-1
    print *,ii
   end do
  end do

!tune$ inject: nb = NB !nb=NB
!tune$ inject_r: nb = NB ! nb=NB
!tune$ inject_r$: nb = ${NB} ! nb=NB
!tune$ inject_r$: nb = $NB ! nb=NB
!tune$ if (NB > 80) inject_r: nb = NB * NBC ! nb=NB*NBC


  end
