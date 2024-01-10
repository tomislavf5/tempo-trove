import math

# Ovo je od stressed out i prosjeka preporucenih
# odabrani = [
#     0,
#     0.734000027179718,
#     0.6370000243186951,
#     0.3636400103569031,
#     0.7089999914169312,
#     0,
#     0.458050012588501,
#     0.046390000730752945,
#     0.000019999999494757503,
#     0.11315999925136566,
#     0.6480000019073486,
#     0.6988800168037415,
#     0.33647000789642334,
#     1,
#     0.8913000226020813
# ]

# preporuka =  [
#     0.14285714285714285,
#     0.7057857130255017,
#     0.6548571458884648,
#     0.41558786588055746,
#     0.6944007064614978,
#     0.0,
#     0.45107857244355337,
#     0.046819286820079596,
#     0.00004714285673149529,
#     0.1853642841534955,
#     0.6720714271068573,
#     0.6453364342451096,
#     0.3533557142530169,
#     1.0,
#     0.8680114330989974,
# ]

# Od DIWK i SOOI i prosjeka preporuka
odabrani = [
    0.0,
   0.6379999816417694,
   0.5850000083446503,
   0.45454999804496765,
   0.678600013256073,
   0.5,
   0.305089995265007,
   0.21837499737739563,
   0.00013000000035390258,
   0.31296999752521515,
   0.638499990105629,
   0.44208501279354095,
   0.3872449994087219,
   1.0,
   0.8478299975395203
]

preporuka =  [
    0.0,
    0.6676428616046906,
    0.6737857162952423,
    0.5064942751611982,
    0.6882399916648865,
    1.0,
    0.3345178578581129,
    0.21507500005619867,
    0.0029942857062061584,
    0.3660042850034578,
    0.6405714239392962,
    0.46570357254573275,
    0.40975500430379597,
    1.0,
     0.9254649962697711
]

def srednja_ag(odabrani, preporuka):
   greska = 0.0
   for i in range(len(odabrani)):
       greska += abs(preporuka[i] - odabrani[i])
   return greska / len(odabrani)

def srednja_kg(odabrani, preporuka):
   greska = 0.0
   for i in range(len(odabrani)):
       odstupanje = preporuka[i] - odabrani[i]
       greska += (odstupanje ** 2)
   return greska / len(odabrani)

def korijen_srednje_kg(odabrani, preporuka):
   greska = 0.0
   for i in range(len(odabrani)):
       odstupanje = preporuka[i] - odabrani[i]
       greska += (odstupanje ** 2)
   return math.sqrt(greska / len(odabrani))


sag = srednja_ag(odabrani, preporuka)
skg = srednja_kg(odabrani, preporuka)
kskg = korijen_srednje_kg(odabrani, preporuka)
print("Srednja apsolutna greška: ", sag)
print("Srednja kvadratna greška: ", skg)
print("Korijen srednje kvadratne greške: ", kskg)
