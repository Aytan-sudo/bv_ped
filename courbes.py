#%%
import lib
import pandas
import numpy as np
import matplotlib.pyplot as plt

"""
TODO
"""
def graph(virus):
    df = pandas.read_pickle('databases\\file.pkl')

    #Préparation des variables utiles pour le graphe
    order_weeks = [i for i in range(35,54)]
    for i in range(1,35):
        order_weeks.append(i)
    order_weeks_str = [str(x) for x in order_weeks]
    xi = list(range(len(order_weeks_str)))
    order_month = ["Sept.","Oct.","Nov.","Dec.","Jan.","Fev.","Mar.","Avr.","Mai","Juin","Jui.", "Aout"]
    pos_month = [1,5,9,14,18,23,27,31,36,40,44,49] #Numéro de semaine des débuts de mois

    hiver_hist = lib.hiver_hist
    hiver_en_cours = lib.hiver_en_cours
    periode = hiver_hist + hiver_en_cours

#Mise en forme du tableau avant mise sous graphe

    df = df.loc[df[str(virus)] == True]
    db = df.groupby(["date"]).size() #Nombre de valeur date de consult
    db = db.reindex(pandas.date_range(start = min(df["date"]), end = max(df["date"]))) #Augmenter l'index avec min et max date
    db = db.fillna(0) #Mettre les valeur NA à 0 et réindexer

    db = db.to_frame(name = "count")
    db["week"] = db.index.isocalendar().week
    db["year"] = db.index.year
    db["date"] = db.index.date
    db["month"] = db.index.month
    db["winter_year"] = db["date"].apply(lib.winter_year)

    #Passage en pivot_table
    #db_hist c'est l'historique ancien
    db_hist = db.loc[db["winter_year"].isin(hiver_hist)]
    dbpiv_hist = pandas.pivot_table(db_hist,values = ["count"],index = ["week"], columns = ["winter_year"],aggfunc=np.sum)
    dbpiv_hist = dbpiv_hist.reindex(order_weeks).fillna(method = "ffill", limit=1)
    dbpiv_hist.index = [str(x) for x in order_weeks]

    #db_act c'est l'hiver actuel
    db_act = db.loc[db["winter_year"].isin(hiver_en_cours)]
    dbpiv_act = pandas.pivot_table(db_act,values = ["count"],index = ["week"], columns = ["winter_year"],aggfunc=np.sum)
    dbpiv_act = dbpiv_act.reindex(order_weeks).fillna(method = "bfill", limit=1)
    dbpiv_act.index = [str(x) for x in order_weeks]

    dbpiv_hist.plot(use_index=True,
                linewidth = 1,
                #color = lib.color_graphs["hist"],
                color = plt.cm.plasma(np.linspace(0.9, 0.1, 4)),
                figsize = (11.69,8.27),
                fontsize = 14)
    plt.plot(dbpiv_act, lib.color_graphs[virus], linewidth=3)
    plt.legend(periode, fontsize = 14)
    plt.suptitle(f"Analyse des {lib.names_virus[virus]}",fontsize = 22)
    plt.title(f"Dernier cas détecté le {max(df['date']).strftime('%d/%m/%Y')}, en semaine {max(df['date']).strftime('%W')}",fontsize = 14, pad = 15)
    plt.xlabel("Numéro de semaine", fontsize = 16)
    plt.ylabel("Total", fontsize = 16)
    plt.xticks(range(0,53,3), order_weeks_str[::3])
    ax = plt.gca()
    secax = ax.secondary_xaxis(0.04)
    secax.spines['bottom'].set_color('white')
    secax.set_xticks(pos_month, order_month)
    secax.tick_params(length = 0)

    plt.savefig(f"courbes\{virus}.pdf")
    plt.savefig(f"courbes\daybyday\{max(df['date']).strftime('%Y_%m_%d')}_{virus}.pdf")


