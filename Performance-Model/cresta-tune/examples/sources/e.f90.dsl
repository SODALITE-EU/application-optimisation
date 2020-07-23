  program a
  integer, parameter :: n=10000
  integer P,Q,nb

  nb = 4
!tune$ param define P type int range 2,4,8 
!tune$ param define Q type int constraint Q = 16/P
!tune$ param constraint Q>2

!tune$ begin replace
  print *,P,Q
!tune$ end replace
  end
