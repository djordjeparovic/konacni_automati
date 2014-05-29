#!/usr/bin/python

import sys, re, itertools
from itertools import groupby

prvi_automat_file = ""
drugi_automat_file = ""
if not len(sys.argv) == 3:
	print "Skript treba da primi 2 argumenta: dve datoteke koje sadrze opis automata."
	exit()
else:
	prvi_automat_file = sys.argv[1]
	drugi_automat_file = sys.argv[2]

try:
    prvi_automat = open(prvi_automat_file, "r")
except (IOError):
    print "Neuspesno otvaranje fajla " + prvi_automat_file + "."
    exit()

try:
    drugi_automat = open(drugi_automat_file, "r")
except (IOError):
    print "Neuspesno otvaranje fajla " + drugi_automat_file + "."
    exit()

def nije_komentar(l):
    return l[0] != '#' and l!='\n'

tmp = prvi_automat.readlines()
prvi_automat_linije = filter(nije_komentar, tmp)
tmp = drugi_automat.readlines()
drugi_automat_linije = filter(nije_komentar, tmp)

struktura_prvog_automata = []
struktura_drugog_automata = []

#odredjivanje azbuke automata
tmp = re.split("," , prvi_automat_linije[0].strip())
azbuka = [s.strip() for s in tmp]
struktura_prvog_automata.append(azbuka)

tmp = re.split("," , drugi_automat_linije[0].strip())
azbuka = [s.strip() for s in tmp]
struktura_drugog_automata.append(azbuka)
#odredjivanje stanja automata
tmp = re.split("," , prvi_automat_linije[1].strip())
stanja = [s.strip() for s in tmp]
struktura_prvog_automata.append(stanja)

tmp = re.split("," , drugi_automat_linije[1].strip())
stanja = [s.strip() for s in tmp]
struktura_drugog_automata.append(stanja)
#pocetno/a stanja
tmp = re.split(",", prvi_automat_linije[2].strip())
pocetna_stanja = [s.strip() for s in tmp]
struktura_prvog_automata.append(pocetna_stanja)


if len(pocetna_stanja) != 1:
	print "Automat nije deterministicki."
	exit()

tmp = re.split(",", drugi_automat_linije[2].strip())
pocetna_stanja = [s.strip() for s in tmp]
struktura_drugog_automata.append(pocetna_stanja)
if len(pocetna_stanja) != 1:
        print "Automat nije deterministicki."
        exit()
#zavrsna stanja 
tmp = re.split(",", prvi_automat_linije[3].strip())
zavrsna_stanja = [s.strip() for s in tmp]
struktura_prvog_automata.append(zavrsna_stanja)

tmp = re.split(",", drugi_automat_linije[3].strip())
zavrsna_stanja = [s.strip() for s in tmp]
struktura_drugog_automata.append(zavrsna_stanja)
#prelazi automata
prelazi = [re.split("\s+", s) for s in [s.strip() for s in prvi_automat_linije[4:]] ]
struktura_prvog_automata.append(prelazi)

prelazi = [re.split("\s+", s) for s in [s.strip() for s in drugi_automat_linije[4:]] ]
struktura_drugog_automata.append(prelazi)

def prelaz_po_reci(automat, stanje, rec): # struktura automata & rec kao torka
	prelazi = automat[4] # lista
	trenutno_stanje = stanje
	for slovo in rec:
		for p in prelazi:
			if p[0] == str(trenutno_stanje) and p[1] == slovo:
				trenutno_stanje = p[2]
				break
	return trenutno_stanje # element liste stanja

# za skup stanja i neko stanje, odredjuje da li stanje ima isti skup rezultujucih stanja po 
# odredjenoj duzini reci. True ako je skupe rezultujucih stanja datog stanja jednak svakom el
# liste gde su clanovi skupovi rezultujucih stanja svakog stanja iz klase
def stanje_se_uklapa_u_klasu(stanje, automat, klasa, duzina_reci): 
  test_reci = [s for s in itertools.product(automat[0], repeat=duzina_reci)]
  skupovi_prelaza_u_klasi = []
  skupovi_prelaza_iz_stanja_tmp = []
  tmp_rez = True
  for i in range(0, len(klasa)):
    tmp = []
    for r in test_reci:
      tmp.append(prelaz_po_reci(automat, klasa[i], r))
      skupovi_prelaza_iz_stanja_tmp.append(prelaz_po_reci(automat, stanje, r))
    skupovi_prelaza_u_klasi.append(list(set(tmp)))
    skupovi_prelaza_iz_stanja = list(set(skupovi_prelaza_iz_stanja_tmp))
  for skup in skupovi_prelaza_u_klasi:
    tmp_rez = tmp_rez and skupovi_prelaza_iz_stanja == skup
  if tmp_rez:
    return True
  else:
    return False

def stanje_u_skup(automat, stanje, test_reci):
  return [prelaz_po_reci(automat, stanje, rec) for rec in test_reci ] #lista stanja u koja moze da se predje

def skup_u_skup(automat, skup_stanja): # za skup stanja, vraca broj skupova koliko ima slova
 # test_reci = [s for s in itertools.product(automat[0], repeat=1)]
  # na ovom mestu automat moze da bude nedetrministicki
  #print skup_stanja
  rezultat = []
  for st in skup_stanja:
  
    klase = {}
   # print automat[0]
    for s in automat[0]:
      klase[s] = []
    for prelaz in automat[4]:
      if prelaz[0] in skup_stanja:
        klase[prelaz[1]].append(prelaz[2])
    for sta in klase.values():
      rezultat.append(sta)
  return [k for k,v in groupby(sorted(rezultat))]
    
def prelazi_unutar_klase_po_slovu(automat, klasa, slovo):
  rezultat = []
  for stanje in klasa:
    for prelaz in automat[4]:
      if prelaz[0] == stanje and prelaz[1] == slovo:
	rezultat.append(prelaz[2])
  return rezultat

###   determinizacija   ##
def determinizovani_automat(automat):
  novo_pocetno_stanje = automat[2]
  odradjena_stanja = []
  neodradjena_stanja = [novo_pocetno_stanje]
  neodradjena_stanja_tmp = neodradjena_stanja
  while neodradjena_stanja_tmp != []:
    neodradjena_stanja_tmp = []
    for n in neodradjena_stanja:
      n.sort()
    for i in range(0, len(neodradjena_stanja)):
      if not neodradjena_stanja[i] in odradjena_stanja:
        odradjena_stanja.append(neodradjena_stanja[i])
      tmp = skup_u_skup(automat, neodradjena_stanja[i])
      for t in tmp:
	t.sort()
        if not t in neodradjena_stanja and not t in odradjena_stanja:
	  neodradjena_stanja_tmp.append(t)
    neodradjena_stanja = neodradjena_stanja_tmp	
  nova_stanja_automata_tmp = odradjena_stanja # u obliku klasa jos ce se preimenovati
  # podaci za pakovanje novog automata
  nova_stanja_automata = [str(i) for i in range(0, len(nova_stanja_automata_tmp))]
  novo_pocetno_stanje = [str(i) for i in range(0, len(nova_stanja_automata_tmp)) if nova_stanja_automata_tmp[i] == novo_pocetno_stanje]
  nova_zavrsna_stanja_tmp = []
  for z in automat[3]:
    for st in nova_stanja_automata_tmp:
      if z in st:
	nova_zavrsna_stanja_tmp.append(st)
  nova_zavrsna_stanja = [str(i) for i in range(0, len(nova_stanja_automata_tmp)) if nova_stanja_automata_tmp[i] in nova_zavrsna_stanja_tmp]

  prelazi_novog_automata_tmp = []
  
  for stanje in nova_stanja_automata_tmp:
    for slovo in automat[0]:
      prelazi_novog_automata_tmp.append([stanje, slovo, prelazi_unutar_klase_po_slovu(automat, stanje, slovo)])
# print prelazi_novog_automata_tmp # ispisuje prelaze izmedju klasa
  prelazi_novog_automata = []
  for prelaz in prelazi_novog_automata_tmp:
    stanje_in_tmp = prelaz[0]
    stanje_out_tmp = prelaz[2]
    for i in range(0, len(nova_stanja_automata_tmp)):
      if nova_stanja_automata_tmp[i] == stanje_in_tmp:
	stanje_in = str(i)
	break
    for i in range(0, len(nova_stanja_automata_tmp)):
      if nova_stanja_automata_tmp[i] == stanje_out_tmp:
	stanje_out = str(i)
	break
    prelazi_novog_automata.append([stanje_in, prelaz[1], stanje_out])
  return [automat[0], nova_stanja_automata, novo_pocetno_stanje, nova_zavrsna_stanja, prelazi_novog_automata]

def minimalizovani_automat(automat): #vraca minimalizovani automat od datog deterministickog automata
  zavrsna_stanja = automat[3]
  nezavrsna_stanja = [s for s in automat[1] if not s in zavrsna_stanja]
  klase_automata = [nezavrsna_stanja, zavrsna_stanja]
  nove_klase_automata = []
  broj_klasa_stari = 0
  broj_klasa_novi = 2
  duzina_test_reci = 0
  
# WHILE petlja razbija sve klase na vise manjih klasa
  while broj_klasa_novi != broj_klasa_stari:
    duzina_test_reci += 1
 ### deo koji radi posao za odredjenu duzinu reci
    test_reci = [s for s in itertools.product(automat[0], repeat=duzina_test_reci)]
    for kl in klase_automata:
   #   print "broj klasa : " + str(broj_klasa_novi) + "--------" + str(broj_klasa_stari)
  #################      razbijanje klase na na vise klasi       ################
      mapa_klasa_tmp = {}
      for st in kl: 
        mapa_klasa_tmp[st] = stanje_u_skup(automat, st, test_reci)
      vrednosti_tmp = mapa_klasa_tmp.values()
      vrednosti = [k for k,v in groupby(sorted(vrednosti_tmp))]
      mapa_klasa = []
      for k in vrednosti:
        mapa_klasa.append([p for p in mapa_klasa_tmp.keys() if mapa_klasa_tmp[p] == k])
 ################# kraj dela koda koji razbija klase na vise klasi ###############
      for k in mapa_klasa:
        nove_klase_automata.append(k)
      tmp = nove_klase_automata
      nove_klase_automata = [k for k,v in groupby(sorted(tmp))]
      broj_klasa_stari = broj_klasa_novi
      broj_klasa_novi = len(nove_klase_automata)
# kraj dela koji radi posao za odredjenu duzinu reci && kraj za WHILE
  #stanja numerisemo brojevima (indeks klasa u nizu novih klasa)
  nova_stanja = [str(i) for i in range(0, len(nove_klase_automata))]
  for i in range(0, len(nove_klase_automata)):
    if automat[2][0] in nove_klase_automata[i]:
      nova_pocetna_stanja = [str(i)]
      break
  nova_zavrsna_stanja = []
  for s in automat[3]: #zavrsna stanja
    for i in range(0, len(nove_klase_automata)):
      if s in nove_klase_automata[i]:
	if not str(i) in nova_zavrsna_stanja: 
	  nova_zavrsna_stanja.append(str(i))
 # za ulazni automat se pretpostavlja da je deterministicki (potpun)
  novi_prelazi_automata_tmp = []
  for prelaz in automat[4]:
    #za stanje treba odrediti klasu
    stanje_in_tmp = prelaz[0]
    stanje_out_tmp = prelaz[2]
    for i in range(0, len(nove_klase_automata)):
      if stanje_in_tmp in nove_klase_automata[i]:
	stanje_in = str(i)
	break
    for i in range(0, len(nove_klase_automata)):
      if stanje_out_tmp in nove_klase_automata[i]:
	stanje_out = str(i)
	break
    novi_prelazi_automata_tmp.append([stanje_in, prelaz[1], stanje_out])
    novi_prelazi_automata = [k for k,v in groupby(sorted(novi_prelazi_automata_tmp))]
    #### KRAJ minimalizacije
  izlazni_automat = [automat[0], nova_stanja, nova_pocetna_stanja, nova_zavrsna_stanja, novi_prelazi_automata]
  return izlazni_automat

#	proizvod dva automata, od dva automata pravi novi koji je dobijen kao prozivod ta dva
# 	ulaz su dva automata, i opis proizvoda u obliku stringa: 'unija' | 'presek' | 'razlika'
# 	gde razlika podrazumeva razlika prvog / drugi_automat
# 	izlaz je struktura novog automata
def proizvod_automata(automatA, automatB, opis):
  stanja_novog_automata_tmp = list(itertools.product(automatA[1],automatB[1])) # sadrzi listu parova
  #prenumerisemo stanja zbog lepseg zapisa
  stanja_novog_automata = [str(i) for i in range(0, len(stanja_novog_automata_tmp))] #novom stanju 'i', odg stanje 
  # iz liste, stanja_novog_automata_tmp[i]
  for i in range(0, len(stanja_novog_automata_tmp)):
    if stanja_novog_automata_tmp[i] == (automatA[2][0], automatB[2][0]):
      novo_pocetno_stanje = [str(i)]
      break
      
  if opis == "presek":
    nova_zavrsna_stanja_tmp = [(a,b) for (a,b) in stanja_novog_automata_tmp if a in automatA[3] and b in automatB[3]]
  if opis == "unija":
    nova_zavrsna_stanja_tmp = [(a,b) for (a,b) in stanja_novog_automata_tmp if a in automatA[3] or b in automatB[3]]
  if opis == "razlika":
    nova_zavrsna_stanja_tmp = [(a,b) for (a,b) in stanja_novog_automata_tmp if a in automatA[3] and b not in automatB[3]]
  if not opis in ["presek", "unija", "razlika"]:
   # print "Funkcija treba da se pozove proizvod_automata(automatA, automatB, opis) gde je opis 'unija' | 'presek' | 'razlika'"
    exit()
  
  nova_zavrsna_stanja = [str(i) for i in range(0,len(stanja_novog_automata)) if stanja_novog_automata_tmp[i] in nova_zavrsna_stanja_tmp]
  proizvod_prelaza = [s for s in list(itertools.product(automatA[4],automatB[4])) if s[0][1] == s[1][1]]
  novi_prelazi_automata_tmp = []
  for s in proizvod_prelaza:
    novi_prelazi_automata_tmp.append([(s[0][0], s[1][0]), s[0][1], (s[0][2], s[1][2])])
  novi_prelazi_automata = []
  for s in novi_prelazi_automata_tmp:
    for i in range(0, len(stanja_novog_automata)):
      if s[0] == stanja_novog_automata_tmp[i]:
	stanje_in = i
	break
    for i in range(0, len(stanja_novog_automata)):
      if s[2] == stanja_novog_automata_tmp[i]:
	stanje_out = i
	break
    novi_prelazi_automata.append([str(stanje_in), s[1], str(stanje_out)])
    izlazni_automat = [automatA[0], stanja_novog_automata, novo_pocetno_stanje, nova_zavrsna_stanja, novi_prelazi_automata]
  return izlazni_automat

#	ispis automata u latex dokument koji koristi tikz biblioteku
#	ulaz je struktura automata, a izlaz su linije u kojima je zadrzaj izmedju \begin{tkizpicture} i 
# 	\end{tkizpicture} zakljucno, tako da se lako moze napakovati u izlazni tex fajl
def ispis_automata_u_latex(automat):
  stanja_automata = []
  stanja_automata.append(automat[2][0])
  ostala_stanja = [s for s in automat[1] if s not in automat[2] ] # sva stanja osim pocetnog
  for s in ostala_stanja:
    #stanja_automata.append(s[0])
    stanja_automata.append(s)
  linije_izlaza = ["\\begin{tikzpicture}[shorten >=1pt,node distance=2cm,on grid,auto]\n"]
  if stanja_automata[0] in automat[3]:
    linije_izlaza.append("\t\\node[state,initial, accepting] (" + stanja_automata[0]+ ")   {$" +stanja_automata[0]+ "$};\n")
  else:
    linije_izlaza.append("\t\\node[state,initial] (" + stanja_automata[0]+ ")   {$" +stanja_automata[0]+ "$};\n")
  for i in range(1, len(stanja_automata)): #ako je zavrsno stanje
    if stanja_automata[i] in automat[3]:
      linije_izlaza.append("\t\\node[state,accepting]("+ stanja_automata[i]+") [right=of "+ stanja_automata[i-1]+"] {$"+ stanja_automata[i]+"$};\n")
    else:
      linije_izlaza.append("\t\\node[state]("+ stanja_automata[i]+") [right=of "+ stanja_automata[i-1]+"] {$"+ stanja_automata[i]+"$};\n")
  linije_izlaza.append("\t \\path[->]\n")
  for prelaz in automat[4][0:-1]: # sve osim poslednjeg zbog ; na kraju
    if prelaz[0] == prelaz[2]:
      linije_izlaza.append("(" + prelaz[0] + ")" + "edge [loop above] node [swap] {"+prelaz[1]+"} ()\n")
    else:
      linije_izlaza.append("(" + prelaz[0] + ")"+ "edge [bend right] node [swap] {"+prelaz[1]+"} ("+prelaz[2]+")\n")
  if automat[4][-1][0] == automat[4][-1][2]:
    linije_izlaza.append("(" + automat[4][-1][0] + ")" + "edge [loop above] node [swap] {"+automat[4][-1][1]+"} ();\n")
  else:
      linije_izlaza.append("(" + automat[4][-1][0] + ")" + "edge [bend right] node [swap] {"+automat[4][-1][1]+"} ("+automat[4][-1][2]+");\n")
  linije_izlaza.append("\\end{tikzpicture}")
  return linije_izlaza


### FINALNO (ono sto se trazi u zadatku, za dva automata odrediti MDKA proizvoda unije, preseka i razlike, i odstampati)

prvi_automat_minimalizovan = minimalizovani_automat(determinizovani_automat(struktura_prvog_automata))
drugi_automat_minimalizovan = minimalizovani_automat(determinizovani_automat(struktura_drugog_automata))
proizvod_automata_presek = proizvod_automata(prvi_automat_minimalizovan, drugi_automat_minimalizovan, "presek")
proizvod_automata_unija = proizvod_automata(prvi_automat_minimalizovan, drugi_automat_minimalizovan, "unija")
proizvod_automata_razlikaAB = proizvod_automata(prvi_automat_minimalizovan, drugi_automat_minimalizovan, "razlika")
proizvod_automata_razlikaBA = proizvod_automata(drugi_automat_minimalizovan, prvi_automat_minimalizovan, "razlika")
zaglavlje_latex_dokumenta = "\\documentclass{article}\n\\usepackage[margin=1in,footskip=0.25in]{geometry}\n\\usepackage{tikz}\n\\usetikzlibrary{automata,positioning}\n\\begin{document}"
podnozje_latex_dokumenta = "\n\\end{document}"

  	#ispis linija u izlazni .tex fajla
  	#prevodjenje u .pdf se moze uraditi online, ovaj sajt sadrzi sve potrebne biblioteke:
  	#http://latex.informatik.uni-halle.de/latex-online/latex.php
izlazna_datoteka = open('izlazni_fajl.tex','w')


#print zaglavlje_latex_dokumenta
izlazna_datoteka.write(zaglavlje_latex_dokumenta)
#print "\\section{Prvi automat}"
izlazna_datoteka.write("\\section{Prvi automat}")
for linija in ispis_automata_u_latex(struktura_prvog_automata):
 # print linija,
  izlazna_datoteka.write(linija)
#print "\\section{Drugi automat}"
izlazna_datoteka.write("\\section{Drugi automat}")
for linija in ispis_automata_u_latex(struktura_drugog_automata):
 # print linija,
  izlazna_datoteka.write(linija)
#print "\\section{Presek automata}"
izlazna_datoteka.write("\\section{Presek automata}")
for linija in ispis_automata_u_latex(minimalizovani_automat(proizvod_automata_presek)):
 # print linija,
  izlazna_datoteka.write(linija)
#print "\\section{Unija automata}"
izlazna_datoteka.write("\\section{Unija automata}")
for linija in ispis_automata_u_latex(minimalizovani_automat(proizvod_automata_unija)):
 # print linija,
  izlazna_datoteka.write(linija)
#print "\\section{Razlika automata A/B}"
izlazna_datoteka.write("\\section{Razlika automata A/B}")
for linija in ispis_automata_u_latex(minimalizovani_automat(proizvod_automata_razlikaAB)):
 # print linija,
  izlazna_datoteka.write(linija)
#print "\\section{Razlika automata B/A}"
izlazna_datoteka.write("\\section{Razlika automata B/A}")
for linija in ispis_automata_u_latex(minimalizovani_automat(proizvod_automata_razlikaBA)):
 # print linija,
  izlazna_datoteka.write(linija)
#print podnozje_latex_dokumenta
izlazna_datoteka.write(podnozje_latex_dokumenta)

print "Zavrseno pisanje izlazne datoteke izlazni_fajl.tex."
izlazna_datoteka.close()
