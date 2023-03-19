import psycopg2 as pg2
import pandas as pd
import ast
import dateparser
import traceback
import math

#only work in wsl

connection = pg2.connect(user="user", password="1234", host="localhost", port="5432", database="postgres")
df = pd.read_csv("data/steam_final.csv")
valid_ids = {}

categoria = {} #(appid, cat)
cont_categoria = 0
genero = {} #(appid, gen)
cont_genero = 0
empresa  = {} #[(appid,des), (appid, distr)]
cont_empresa = 0
tag  = {} #(appid, tag, quant)
cont_tag = 0
lingua  = {} #(appid, lingua)
cont_lingua = 0
jogo  = {} #
dlc = {} #

def get(command):
    with connection.cursor() as cur:
        print("VAI EXECUTAR")
        cur.execute(command)
        print("EXECUTOU")
        infos = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
    return infos, colnames

def execute(command):
    with connection.cursor() as cur:
        cur.execute(command)
    connection.commit()

def create_tables():
    execute(open("database/tables.sql", "r").read())
    #open("database/tables.sql", "r")
    #execute("DROP TABLE App;")
    #print(get("SELECT * FROM Lingua;"))
    #print(execute("INSERT INTO Lingua (nome) VALUES ('daleson');"))
    #print(get("SELECT * FROM Lingua;"))
    #execute("CREATE TABLE App (id SERIAL NOT NULL PRIMARY KEY);")
    #execute("CREATE TABLE App (id SERIAL NOT NULL PRIMARY KEY,    nome VARCHAR(100) NOT NULL,    preco DECIMAL(6,2) NOT NULL,    data_lancamento DATE NOT NULL,    analises_positivas INTEGER NOT NULL,    analises_negativas INTEGER NOT NULL,    windows_support BOOLEAN NOT NULL,     linux_support BOOLEAN NOT NULL,     mac_support BOOLEAN NOT NULL);")

def insert_app():
    cont = -1
    cont_categoria = 0
    cont_genero = 0
    cont_empresa = 0
    cont_tag = 0
    cont_lingua = 0
    with connection.cursor() as cur:
        for _, i in df.iterrows():
            try:
                query = """INSERT INTO App (id, nome, preco, data_lancamento, analises_positivas, analises_negativas, windows_support, linux_support, mac_support) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                # id, nome, preco, data_lancamento, analises_positivas, analises_negativas, windows_support, linux_support, mac_support
                #print(i)
                if pd.isna(i["release_date"]):
                    continue
                rel_date = ast.literal_eval(i["release_date"])
                if rel_date["date"] == '' or rel_date["date"] in ["Coming soon", "To be announced", "None"] :
                    continue
                if rel_date["coming_soon"] == True:
                    continue
                if pd.isna(i["name"]):
                    continue
                #s = rel_date["date"][:-4]
                #if all(x not in s for x in "0123456789"):
                #    rel_date["date"] = rel_date["date"][:-4] + "1, " + rel_date["date"][-4:]
                rel_date["date"] = str(dateparser.parse(rel_date["date"]))
                plats = ast.literal_eval(i["platforms"])
                record = (i["appid"], i["name"], i["initialprice"]/100.0, rel_date["date"], i["positive"], i["negative"] , plats["windows"], plats["linux"], plats["mac"])

                # JOGO
                if i["type"] == "game":
                    jogo[i["appid"]] = True
                # DLC
                elif i["type"] == "dlc" and not pd.isna(i["fullgame"]):
                    fullgame_info = ast.literal_eval(i["fullgame"])
                    dlc[i["appid"]] = int(fullgame_info["appid"])
                else:
                    continue

                # TAG 
                tgs = ast.literal_eval(i["tags"])
                if len(tgs) != 0:
                    for t, quant in tgs.items():
                        if not tag.get(t):
                            tag[t] = {"id":cont_tag, "assoc":[]}
                            cont_tag += 1
                        tag[t]["assoc"].append({"id": i["appid"], "quant": quant})

                # CATEGORIES
                cats = ast.literal_eval(i["categories"])
                for cat in cats:
                    if not categoria.get(cat["description"]):
                        categoria[cat["description"]] = {"id":cont_categoria, "ids":set()}
                        cont_categoria += 1
                    categoria[cat["description"]]["ids"].add(i["appid"])
                
                # GENEROS
                gens = i["genre"].split(",")
                for gen in gens:
                    gen = gen.strip()
                    if not genero.get(gen):
                        genero[gen] = {"id":cont_genero, "ids":set()}
                        cont_genero += 1
                    genero[gen]["ids"].add(i["appid"])

                # EMPRESA
                devs = ast.literal_eval(i["developers"])
                for dev in devs:
                    if not empresa.get(dev):
                        empresa[dev] = {"id":cont_empresa, "dev":set(), "distr":set()}
                        cont_empresa += 1
                    empresa[dev]["dev"].add(i["appid"])
                dists = ast.literal_eval(i["publishers"])
                for dist in dists:
                    if not empresa.get(dist):
                        empresa[dist] = {"id":cont_empresa, "dev":set(), "distr":set()}
                        cont_empresa += 1
                    empresa[dist]["distr"].add(i["appid"])

                #LINGUA
                lings = i["languages"].split(",")
                for ling in lings:
                    ling = ling.strip()
                    if not lingua.get(ling):
                        lingua[ling] = {"id":cont_lingua, "ids":set()}
                        cont_lingua += 1
                    lingua[ling]["ids"].add(i["appid"])
                

                cur.execute(query, record)
                valid_ids[i["appid"]] = i
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
                #TESTING
                #if cont % 99999 == 10000:
                #    break
            except Exception as e:
                print(e)
                print(i)
                traceback.print_exc()
                exit(0)

        connection.commit()
        print(f"{len(valid_ids)} inserted total")

def insert_categoria():
    cont = 0
    with connection.cursor() as cur:
        for name, item in categoria.items():
            query = """INSERT INTO Categoria (id, nome) VALUES (%s,%s)"""
            record = (item["id"], name)
            cur.execute(query, record)
            for id in item["ids"]:
                query = """INSERT INTO Categorizacao (fk_Categoria_id, fk_App_id) VALUES (%s,%s)"""
                record = (item["id"], id)
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
        connection.commit()

def insert_genero():
    cont = 0
    with connection.cursor() as cur:
        for name, item in genero.items():
            query = """INSERT INTO Genero (id, nome) VALUES (%s,%s)"""
            record = (item["id"], name)
            cur.execute(query, record)
            for id in item["ids"]:
                query = """INSERT INTO Classificacao (fk_Genero_id, fk_App_id) VALUES (%s,%s)"""
                record = (item["id"], id)
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
        connection.commit()

def insert_empresa():
    cont = 0
    with connection.cursor() as cur:
        for name, item in empresa.items():
            query = """INSERT INTO Empresa (id, nome) VALUES (%s,%s)"""
            record = (item["id"], name)
            cur.execute(query, record)
            for id in item["dev"]:
                query = """INSERT INTO Desenvolvedora (fk_Empresa_id, fk_App_id) VALUES (%s,%s)"""
                record = (item["id"], id)
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
            for id in item["distr"]:
                query = """INSERT INTO Distribuidora (fk_Empresa_id, fk_App_id) VALUES (%s,%s)"""
                record = (item["id"], id)
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
        connection.commit()

def insert_tag():
    cont = 0
    with connection.cursor() as cur:
        for name, item in tag.items():
            query = """INSERT INTO Tag (id, nome) VALUES (%s,%s)"""
            record = (item["id"], name)
            cur.execute(query, record)
            for assoc in item["assoc"]:
                query = """INSERT INTO Tags (fk_Tag_id, fk_App_id, quantidade) VALUES (%s,%s, %s)"""
                record = (item["id"], assoc["id"], assoc["quant"])
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
        connection.commit()

def insert_lingua():
    cont = 0
    with connection.cursor() as cur:
        for name, item in lingua.items():
            query = """INSERT INTO Lingua (id, nome) VALUES (%s,%s)"""
            record = (item["id"], name)
            cur.execute(query, record)
            for id in item["ids"]:
                query = """INSERT INTO Idioma (fk_Lingua_id, fk_App_id) VALUES (%s,%s)"""
                record = (item["id"], id)
                cur.execute(query, record)
                cont += 1
                if cont % 1000 == 0:
                    print(f"{cont} inserted.")
        connection.commit()

def insert_jogo():
    cont = 0
    with connection.cursor() as cur:
        for id, _ in jogo.items():
            query = """INSERT INTO Jogo (id) VALUES (%s)"""
            record = (id,)
            cur.execute(query, record)
            cont += 1
            if cont % 1000 == 0:
                print(f"{cont} inserted.")
        connection.commit()

def insert_dlc():
    cont = 0
    with connection.cursor() as cur:
        for id, fullgame in dlc.items():
            if not jogo.get(fullgame):
                query = """DELETE FROM app WHERE app.id=%s;"""
                record = (id,)
                cur.execute(query, record)    
                #print(f"delete performed f {id}")
                continue
            query = """INSERT INTO Dlc (id, fk_Jogo_id) VALUES (%s, %s)"""
            record = (id, fullgame)
            cur.execute(query, record)
            cont += 1
            if cont % 1000 == 0:
                print(f"{cont} inserted.")
        connection.commit()



print("Loaded data")
create_tables()
print("Created tables")
insert_app()
print("Inserted apps")
insert_categoria()
print("Inserted categorias")
insert_genero()
print("Inserted generos")
insert_empresa()
print("Inserted empresas")
insert_tag()
print("Inserted tags")
insert_lingua()
print("Inserted linguas")
insert_jogo()
print("Inserted jogos")
insert_dlc()
print("Inserted dlcs")
print("Done")
