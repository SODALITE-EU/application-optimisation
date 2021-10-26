DEBUT(LANG='EN')


mesh3 = LIRE_MAILLAGE(identifier=u'0:1',
                      UNITE=2,
                      VERI_MAIL=_F(VERIF='OUI'))

model = AFFE_MODELE(identifier=u'1:1',
                    AFFE=(_F(MODELISATION=('3D', ),
                             PHENOMENE='MECANIQUE',
                             TOUT='OUI'),
                          _F(GROUP_MA=('FixElems', ),
                             MODELISATION=('POU_D_E', ),
                             PHENOMENE='MECANIQUE')),
                          DISTRIBUTION=_F(
                             METHODE='CENTRALISE'
                          ),
                    MAILLAGE=mesh3)

elemprop = AFFE_CARA_ELEM(identifier=u'2:1',
                          MODELE=model,
                          POUTRE=_F(CARA=('HY', 'HZ'),
                                    GROUP_MA=('FixElems', ),
                                    SECTION='RECTANGLE',
                                    VALE=(1.0, 1.0)))

Bone = DEFI_MATERIAU(identifier=u'3:1',
                     ELAS=_F(E=5600.0,
                             NU=0.3))

FixMat = DEFI_MATERIAU(identifier=u'4:1',
                       ELAS=_F(E=1000.0,
                               NU=0.3))

Cartilag = DEFI_MATERIAU(identifier=u'5:1',
                         ELAS=_F(E=1000.0,
                                 NU=0.49))

fieldmat = AFFE_MATERIAU(identifier=u'6:1',
                         AFFE=(_F(GROUP_MA=('GrMesh_V1_Volumes', ),
                                  MATER=(Bone, )),
                               _F(GROUP_MA=('GrMesh_IVD1_Volumes', ),
                                  MATER=(Cartilag, )),
                               _F(GROUP_MA=('FixElems', ),
                                  MATER=(FixMat, )),
                               _F(GROUP_MA=('GrMesh_V2_Volumes', ),
                                  MATER=(Bone, )),
                               _F(GROUP_MA=('GrMesh_IVD2_Volumes', ),
                                  MATER=(Cartilag, )),
                               _F(GROUP_MA=('GrMesh_V3_Volumes', ),
                                  MATER=(Bone, ))),
                         MAILLAGE=mesh3,
                         MODELE=model)

Time_Fun = DEFI_FONCTION(identifier=u'7:1',
                         NOM_PARA='INST',
                         VALE=(0.0, 0.0, 1.0, 1.0))

TimeStep = DEFI_LIST_REEL(identifier=u'8:1',
                          DEBUT=0.0,
                          INTERVALLE=_F(JUSQU_A=1.0,
                                        NOMBRE=10))

V1_LB = AFFE_CHAR_MECA(identifier=u'9:1',
                       DDL_IMPO=_F(DX=0.0,
                                   DY=0.0,
                                   DZ=0.0,
                                   GROUP_NO=('V1_Lower_Nodes', )),
                       MODELE=model)

V2_UL = AFFE_CHAR_MECA(identifier=u'10:1',
                       FORCE_NODALE=_F(FZ=-4.0,
                                       GROUP_NO=('V3_Upper_Nodes', )),
                       MODELE=model)

contact = DEFI_CONTACT(identifier=u'11:1',
                       FORMULATION='DISCRETE',
                       MODELE=model,
                       RESI_ABSO=1e-06,
                       ZONE=(_F(ALGO_CONT='GCP',
                                GROUP_MA_ESCL=('V1_Upper', ),
                                GROUP_MA_MAIT=('IVD_Lower', )),
                             _F(ALGO_CONT='GCP',
                                GROUP_MA_ESCL=('IVD1_Upper', ),
                                GROUP_MA_MAIT=('V2_Lower', )),
                             _F(ALGO_CONT='GCP',
                                GROUP_MA_ESCL=('IVD2_Lower', ),
                                GROUP_MA_MAIT=('V2_Upper', )),
                             _F(ALGO_CONT='GCP',
                                GROUP_MA_ESCL=('IVD2_Upper', ),
                                GROUP_MA_MAIT=('V3_Lower', ))))

load = AFFE_CHAR_MECA(identifier=u'12:1',
                      DDL_IMPO=(_F(DRX=0.0,
                                   DRY=0.0,
                                   DRZ=0.0,
                                   DX=0.0,
                                   DY=0.0,
                                   DZ=0.0,
                                   GROUP_NO=('FixNodes', )),
                                _F(DX=0.0,
                                   DY=0.0,
                                   GROUP_NO=('xy_FixNodes', ))),
                      MODELE=model)

resnonl0 = STAT_NON_LINE(identifier=u'13:1',
                         CARA_ELEM=elemprop,
                         CHAM_MATER=fieldmat,
                         CONTACT=contact,
                         EXCIT=(_F(CHARGE=V2_UL,
                                   FONC_MULT=Time_Fun),
                                _F(CHARGE=V1_LB,
                                   TYPE_CHARGE='FIXE_CSTE'),
                                _F(CHARGE=load,
                                   TYPE_CHARGE='FIXE_CSTE')),
                         INCREMENT=_F(LIST_INST=TimeStep),
                         MODELE=model,
                         SOLVEUR=_F(METHODE='MUMPS'))

IMPR_RESU(identifier=u'14:1',
          FORMAT='MED',
          RESU=_F(MAILLAGE=mesh3,
                  RESULTAT=resnonl0,
                  TOUT='OUI'),
          UNITE=80)

FIN()
