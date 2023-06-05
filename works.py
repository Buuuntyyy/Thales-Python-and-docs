import datetime
import binascii
import time
import struct
import threading
from mysql import connector
from fonctions import *

if __name__ == "__main__":
    path_rep = input("Insérer le chemin absolu du fichier .rep : ")
    if len(path_rep) < 2:
        nom_test = input("Entrer un nom pour le test : ")
        date_test = str(datetime.datetime.now())
        valtest2 = (nom_test, date_test)

    else:
        data = lire_rep(path_rep)

        nom_test = data['name']
        date_test = data['date']

    #Ici on vérifie si le nom du test existe deja dans la bdd:
    verif = connector.connect(host="localhost",user="root",password="", database="thales")
    cv = verif.cursor()

    #on vérifie si le nom du test existe deja, si c'est le cas on récupère le test_id
    sql1 = 'SELECT count(*), test_id FROM test WHERE nom_test IN (\'' + nom_test + '\')'
    cv.execute(sql1)
    res = cv.fetchall()
    nb_occ = res[0][0]
    id_test_occ = res[0][1]
    #print(nb_occ, id_test_occ)
    verif.commit()
    verif.close()

    #ensuite, si ca apparaît au moins 1 fois :
    if nb_occ > 0:
        #Il s'agit d'une nouvelle exécution d'un test deja connu, on l'enregistre dans Execution en faisant référence à son test_id
            old = connector.connect(host="localhost",user="root",password="", database="thales")
            old_conn = old.cursor()
            dateEx = str(datetime.datetime.now())
            valexec = (id_test_occ, dateEx)

            sql1=("INSERT INTO execution (id_test, date_exec) VALUES (%s, %s)")
            old_conn.execute(sql1, valexec)
            old.commit()
            old.close()
    else:
        #c'est un nouveau test qui n'a jamais été exécuté, on l'enregistre dans Test et dans Execution
        conn = connector.connect(host="localhost",user="root",password="", database="thales")
        cursor = conn.cursor()
        valtest = (nom_test, date_test)

        sql1 = 'INSERT INTO test(nom_test, date) VALUES(%s, %s)'

        cursor.execute(sql1, valtest)

        req = "SELECT max(test_id) FROM test"
        cursor.execute(req)
        id = (cursor.fetchall()[0][0])
        dateEx = str(datetime.datetime.now())
        valexec = (id, dateEx)
        sql2="INSERT INTO execution (id_test, date_exec) VALUES (%s, %s)"
        #print(id_test_occ)
        cursor.execute(sql2, valexec)
        conn.commit()
        conn.close()

    #on ajoute une condition de vérification : chaque exécution du code python sera stockée dans la table "exécution"
    #En revanche, chacune de ces exécutions sera lié à un test par la relation "id_test", et chaque test aura un identifiant unique.
    #Ainsi un test pourra avoir N exécutions.
    #Pour ce faire, on compare le nom contenu dans l'execution actuelle avec les noms des test déja présent :
    #Si le nom existe deja, alors il s'agira d'une exécution supplémentaire
    #Sinon, il s'agit d'un nouveau test et de sa première exécution.
    if len(path_rep) > 2:
        id_conn = connector.connect(host="localhost",user="root",password="", database="thales")
        cursor = id_conn.cursor()
        req = "SELECT max(test_id) FROM test"
        cursor.execute(req)
        id = (cursor.fetchall()[0][0])
        id_conn.commit()
        id_conn.close()

        conn = connector.connect(host="localhost",user="root",password="", database="thales")
        cursor = conn.cursor()
        valtest3 = (data['Tested SW'], data['Tested SW version'], data['SDB version'], data['SGSE version'], data['date'], data['name'], id)

        sql3 = 'INSERT INTO fichier(type_obsw, version_obsw, version_bds, type_moyen, date_exec, nom, id_test) VALUES(%s, %s, %s, %s, %s, %s, %s)'

        cursor.execute(sql3, valtest3)
        conn.commit()
        conn.close()
    #print("ok")
    conn = connector.connect(host="localhost",user="root",password="", database="thales") #ajouter les valeurs du bench2 et bench3
    cursor = conn.cursor()
    
    sql_exec = "SELECT max(exec_id) FROM execution"
    cursor.execute(sql_exec)
    id_exec = cursor.fetchall()
    extracteur(cursor, id_exec[0][0])
    conn.commit()
    conn.close()