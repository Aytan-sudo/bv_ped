#%%
import lib

from datetime import date
import pandas
import numpy as np


#%%
# Adding data.csv to the 'complete' data.csv, and update it
df_actual = pandas.read_csv("databases\datafull.csv", sep = ";", encoding = "WINDOWS-1252",low_memory=False)
df_new = pandas.read_csv("databases\data.csv", sep = ";", encoding = "WINDOWS-1252",low_memory=False)

# Remove duplicates
df = pandas.concat([df_actual,df_new]).drop_duplicates().reset_index(drop=True)

#for archive, save as database named to date upto
current_day = date.today().strftime('%Y_%m_%d')
df.to_csv(f"databases\\archive\data_{current_day}.csv", sep = ";", encoding = "WINDOWS-1252", index=False)

df.to_csv("databases\datafull.csv", sep = ";", encoding = "WINDOWS-1252", index=False)

#%%
# Nettoyage et recodage des noms de colonnes (on utilise le dict de lib.py)
df.columns = df.columns.str.strip() 
df.columns = df.columns.str.replace(" ","_")
df.rename(columns=lib.nom_cols, inplace=True)

#%%
# Nettoyage des contenus des cases, mise en forme
df = df.replace(r'\n','', regex=True) 
df.dropna(subset=['echantillon'], inplace=True)
df = df.drop(['Unnamed:_0', 'M_GV_AL_GRIPABVRS_INT_2'], axis=1, errors='ignore')

#%%
# Extraction de la colonne "echantillon" pour la convertir en date d'analyse
dft = pandas.DataFrame()
dft["year"] = df["echantillon"].str[0] + df["echantillon"].str[1]
dft["month"] = df["echantillon"].str[2] + df["echantillon"].str[3]
dft["day"] = df["echantillon"].str[5] + df["echantillon"].str[6]
df["date"] = "20" + dft["year"] + "-" + dft["month"] + "-" + dft["day"]
df["date"] = pandas.to_datetime(df["date"], infer_datetime_format=True)
del dft

maxdate = max(df["date"])
if maxdate.isoweekday() == 1:
    df = df[df.date != maxdate]
del maxdate

#%%
# Creation des colonnes year/isoweek/day
df["year"] = df["date"].dt.isocalendar().year
df["week"] = df["date"].dt.isocalendar().week
df["day"] = df["date"].dt.isocalendar().day
df["winter_year"] = df["date"].apply(lib.winter_year)

# Création des colonnes age (en années, jours), age_cat et ped
df["ddn"] = pandas.to_datetime(df["ddn"], format="%d/%m/%Y")
df["age_j"] = ((df.date - df.ddn) / pandas.Timedelta(days=1))
df["age_a"] = df["age_j"]/365.25
df["age_cat"] = pandas.cut(df["age_j"], bins=lib.bins_age_col, labels=lib.labels_age_col)
df.drop(df.loc[df['age_j']>=6575].index, inplace=True) #Supprimer les majeurs

df = df.replace(to_replace=lib.modifs, regex=True)

#%%    
# Création colonne VRS par analyse des champs textes des colonnes concernées
conditions_vrs = [
    (df["tdr"].str.contains("sync|vrs|SYNC|VRS|Sync", na=False)),
    (df["pcr_grippe_vrs_old"].str.contains("sync|vrs|SYNC|VRS|Sync", na=False)),
    (df["M_GV_AL_GRIPABVRS_INT"].str.contains("sync|vrs|SYNC|VRS|Sync", na=False)),
    (df["M_GV_MULTIRESP_VRSA"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_VRSB"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_VRS"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_VRS"].str.contains("pos|POS|Pos", na=False)),
    (df["if_int"].str.contains("sync|vrs|SYNC|VRS|Sync", na=False)),
    (df["M_V_BIODELOC_VRS"].str.contains("pos|POS|Pos|sitif", na=False)),
    (df["M_GV_BD_VRS_INT"].str.contains("sync|vrs|SYNC|VRS|Sync", na=False)),
]
choices_vrs = [True] * len(conditions_vrs)
df["vrs"] = np.select(conditions_vrs, choices_vrs, default=False) #np_select utilise condition et choices correspondant
del conditions_vrs,choices_vrs

#Création colonne entero
conditions_entero = [
    (df["M_GV_BIOFIRE_HEV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_HEV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_HEV"].str.contains("pos|POS|Pos", na=False))
]
choices_entero = [True] * len(conditions_entero)
df["entero"] = np.select(conditions_entero, choices_entero, default=False) #np_select utilise condition et choices correspondant
del conditions_entero,choices_entero

#Création colonne adeno
conditions_adeno = [
    (df["M_GV_BIOFIRE_ADV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_ADV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_ADV"].str.contains("pos|POS|Pos", na=False))
]
choices_adeno = [True] * len(conditions_adeno)
df["adeno"] = np.select(conditions_adeno, choices_adeno, default=False) #np_select utilise condition et choices correspondant
df["adeno"].value_counts()
del conditions_adeno,choices_adeno

#Création colonne flu
conditions_flu = [
    (df["tdr"].str.contains("gripp|INFLUENZ|Influenz|GRIPP|Gripp", na=False)),
    (df["pcr_grippe_vrs_old"].str.contains("gripp|INFLUENZ|Influenz|GRIPP|Gripp", na=False)),
    (df["M_GV_AL_GRIPABVRS_INT"].str.contains("gripp|INFLUENZ|Influenz|GRIPP|Gripp", na=False)),
    (df["M_GV_BD_COMBO_GRAB_INT"].str.contains("gripp|INFLUENZ|Influenz|GRIPP|Gripp", na=False)),
    (df["M_GV_MULTIRESP_GA"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_GAH1"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_GAH3"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_GB"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_GA"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_GB"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_GA"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_GAH"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_GAH1"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_GAH3_2009"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_GB"].str.contains("pos|POS|Pos", na=False)),
    (df["if_int"].str.contains("gripp|INFLUENZ|Influenz|GRIPP|Gripp", na=False)),
    (df["M_V_BIODELOC_GRIPPE_A"].str.contains("pos|POS|Pos|sitif", na=False)),
    (df["M_V_BIODELOC_GRIPPE_B"].str.contains("pos|POS|Pos|sitif", na=False)),
]
choices_flu = [True] * len(conditions_flu)
df["flu"] = np.select(conditions_flu, choices_flu, default=False) #np_select utilise condition et choices correspondant
del conditions_flu,choices_flu


#Création colonne covid
conditions_covid = [
    (df["M_GV_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_AL_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_BD_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_BD_COMBO_SARS_CoV_2_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_CER_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2", na=False)),
    (df["M_V_SARS_COV_2_DELOC_IC_INT"].str.contains("Infection par le SARS-CoV-2", na=False)),
    (df["M_V_SARS_CoV2_INT"].str.contains("Infection possible par le SARS-CoV2", na=False)),
    (df["M_V_BIODELOC_SARS-CoV-2"].str.contains("pos|Pos|POS|sitif", na=False)),
    (df["M_GV_MULTIRESP_SARS-COV-2"].str.contains("pos|Pos|POS|sitif", na=False)),
]
choices_covid = [True] * len(conditions_covid)
df["covid"] = np.select(conditions_covid, choices_covid, default=False) #np_select utilise condition et choices correspondant
del conditions_covid,choices_covid

conditions_covid_no_tdr = [
    (df["M_GV_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_AL_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_BD_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_BD_COMBO_SARS_CoV_2_INT"].str.contains("Infection par le SARS-CoV-2|contagiosité minime|Traces de génome viral|INFECTION", na=False)),
    (df["M_GV_CER_2019_nCoV_INT"].str.contains("Infection par le SARS-CoV-2", na=False)),
    (df["M_V_SARS_COV_2_DELOC_IC_INT"].str.contains("Infection par le SARS-CoV-2", na=False)),
    (df["M_V_SARS_CoV2_INT"].str.contains("Infection possible par le SARS-CoV2", na=False)),
    (df["M_GV_MULTIRESP_SARS-COV-2"].str.contains("pos|Pos|POS|sitif", na=False)),
]
choices_covid_no_tdr = [True] * len(conditions_covid_no_tdr)
df["covid_no_tdr"] = np.select(conditions_covid_no_tdr, choices_covid_no_tdr, default=False) #np_select utilise condition et choices correspondant
del conditions_covid_no_tdr,choices_covid_no_tdr

#Création colonne rota
conditions_rota = [
    (df["vir_dig_INT"].str.contains("ROTAVIRUS|Rotavirus|rotavirus|Rota|rota|ROTA", na=False)),
]
choices_rota = [True] * len(conditions_rota)
df["rota"] = np.select(conditions_rota, choices_rota, default=False) #np_select utilise condition et choices correspondant
del conditions_rota,choices_rota

#Création colonne adeno_dig
conditions_adeno_dig = [
    (df["vir_dig_INT"].str.contains("ADENOVIRUS|ADENO|Adenovirus|Adeno|adeno", na=False)),
]
choices_adeno_dig = [True] * len(conditions_adeno_dig)
df["adeno_dig"] = np.select(conditions_adeno_dig, choices_adeno_dig, default=False) #np_select utilise condition et choices correspondant
del conditions_adeno_dig,choices_adeno_dig

#Création colonne noro
conditions_noro = [
    (df["vir_dig_INT"].str.contains("NOROVIRUS|NORO|Norovirus|Noro|norovirus|noro", na=False)),
]
choices_noro = [True] * len(conditions_noro)
df["noro"] = np.select(conditions_noro, choices_noro, default=False) #np_select utilise condition et choices correspondant
del conditions_noro,choices_noro

#Création colonne hmpv
conditions_hmpv = [
    (df["M_GV_BIOFIRE_HMPV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_HMPV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_HMPV"].str.contains("pos|POS|Pos", na=False))
]
choices_hmpv = [True] * len(conditions_hmpv)
df["hmpv"] = np.select(conditions_hmpv, choices_hmpv, default=False) #np_select utilise condition et choices correspondant
del conditions_hmpv,choices_hmpv

#Création colonne mycoplasme
conditions_myco = [
    (df["M_GV_BIOFIRE_MYCO"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_MYCO"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_MYCO"].str.contains("pos|POS|Pos", na=False))
]
choices_myco = [True] * len(conditions_myco)
df["myco"] = np.select(conditions_myco, choices_myco, default=False) #np_select utilise condition et choices correspondant
del conditions_myco,choices_myco

#Création colonne parainfluenza
conditions_piv = [
    (df["M_GV_BIOFIRE_PIV1"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_PIV2"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_PIV3"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFIRE_PIV4"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_BIOFPNEU_PIV"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_PIV1"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_PIV2"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_PIV3"].str.contains("pos|POS|Pos", na=False)),
    (df["M_GV_MULTIRESP_PIV4"].str.contains("pos|POS|Pos", na=False)),
]
choices_piv = [True] * len(conditions_piv)
df["piv"] = np.select(conditions_piv, choices_piv, default=False) #np_select utilise condition et choices correspondant
del conditions_piv,choices_piv


#Enregistrement de la base pour stockage

df.to_csv("databases\\base_complete.csv", sep = ";", encoding = "latin-1")
df.to_pickle("databases\\file.pkl")

# %%
