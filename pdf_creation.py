#%%
import os
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from datetime import date, timedelta
from PyPDF2 import PdfReader, PdfMerger, PdfWriter

def pages_garde_et_fin():
    logo = matplotlib.image.imread("images\logo.jpg")
    virus_img = matplotlib.image.imread("images\\virus_img.png")
    enfant_toux1 =matplotlib.image.imread("images\enfant_toux1.png")
    enfant_toux2 = matplotlib.image.imread("images\enfant_toux2.jpg")

    plt.figure(figsize = (11.69,8.27)) 
    ax = plt.gca()
    imagebox_1 = OffsetImage(logo, zoom = 0.5, interpolation="hanning")
    ab_1 = AnnotationBbox(imagebox_1, (0.5,0.2), frameon = False)
    ax.add_artist(ab_1)
    imagebox_2 = OffsetImage(virus_img, zoom = 1)
    ab_2 = AnnotationBbox(imagebox_2, (0.7,0.9), frameon = False)
    ax.add_artist(ab_2)
    imagebox_3 = OffsetImage(enfant_toux1, zoom = 1)
    ab_3 = AnnotationBbox(imagebox_3, (0.2,0.9), frameon = False)
    ax.add_artist(ab_3)
    plt.axis('off')
    plt.text(0.5,0.5,"Bulletin des Virus Pédiatriques",ha='center',va='center', fontsize = 28)
    plt.text(0.2,0.4, f"Analyse du {date.today().strftime('%d/%m/%Y')}, pour la semaine {(date.today()-timedelta(weeks=1)).strftime('%W')}", fontsize = 16)
    plt.text(0.65,0.1, "Aymeric Cantais & Sylvie Pillet", fontsize = 12)
    plt.text(0.1,0.1, "Pédiatrie - CHUSE", fontsize = 12)
    plt.savefig("courbes\pages\page_de_garde.pdf")


    plt.figure(figsize = (11.69,8.27)) 
    ax = plt.gca()
    imagebox_4 = OffsetImage(enfant_toux2, zoom = 1)
    ab_4 = AnnotationBbox(imagebox_4, (0.2,0.2), frameon = False)
    ax.add_artist(ab_4)
    imagebox_5 = OffsetImage(virus_img, zoom = 1)
    ab_5 = AnnotationBbox(imagebox_5, (0.7,0.2), frameon = False)
    ax.add_artist(ab_5)
    plt.axis('off')
    plt.text(0.2,0.6,"Analyse réalisée sur la base de l'ensemble des examens virologiques \ndemandés sur les services de Pédiatrie du CHU, pour les enfants mineurs uniquement \n ")
    plt.text(0.2,0.5, "Les courbes sont tracées jusqu'à date du dernier cas détecté pour un virus donné \n(dates mentionnées en en-tête des graphiques)")
    plt.text(0.2,0.4,"")
    plt.savefig("courbes\pages\page_de_fin.pdf")
# %%



def list_pdf_files(directory):
    with os.scandir(directory) as entries:
        return [entry.path for entry in entries if entry.is_file() and entry.name.endswith('.pdf')]
    
def create_pdf():
    pdfs = list_pdf_files('courbes')

    merger = PdfMerger()

    merger.append("courbes\pages\page_de_garde.pdf")
    for pdf in pdfs:
        merger.append(pdf)
    merger.append("courbes\pages\page_de_fin.pdf")

    merger.write("result.pdf")
    merger.close()

    reader = PdfReader("result.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.add_metadata(
        {
            "/Author": "Aymeric CANTAIS",
            "/Creator": "Aymeric CANTAIS & Sylvie PILLET",
            "/Producer": "Urgences Pédiatriques",
            "/Title": "Bulletin des Virus Pédiatriques de Saint Etienne",
            "/Subject": "Analyse des virus identifiés en Pédiatrie au CHU de St Etienne"
        }
    )

    with open(f"BV_Ped_{date.today().strftime('%d_%m_%Y')}.pdf", "wb") as f:
        writer.write(f)
        
    os.remove("result.pdf") 
# %%
create_pdf()