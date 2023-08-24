import subprocess
import time
import courbes
import pdf_creation

"""
TODO
"""

virus_a_tester = [
    "vrs",
    "entero",
    "flu",
    "covid",
    "adeno",
    "covid_no_tdr",
    "adeno_dig",
    "noro",
    "hmpv",
    "piv",
    "myco" ,
    "rota",
]

main_start = time.time()
subprocess.call("main.py", shell=True)
main_duree = (time.time() - main_start)
print(f"Main.py exécuté en {main_duree:.2f} secondes !")

total_virus = 0
for i in virus_a_tester:
    main_start = time.time()
    courbes.graph(i)
    virus_duree = (time.time() - main_start)
    total_virus += virus_duree
    print(f"Analyse de {i} exécuté en {virus_duree:.3f} secondes !")
    
main_start = time.time()
pdf_creation.pages_garde_et_fin()
pdfgarde_duree = (time.time() - main_start)
print(f"Page de garde et de Fin exécuté en {pdfgarde_duree:.3f} secondes !")

main_start = time.time()
pdf_creation.create_pdf()
pdf_duree = (time.time() - main_start)
print(f"Assemblage du PDF exécuté en {pdf_duree:.3f} secondes !")

temps_total = main_duree + total_virus + pdfgarde_duree + pdf_duree

print(f"Durée totale d'exécution : {temps_total:.2f} secondes")

