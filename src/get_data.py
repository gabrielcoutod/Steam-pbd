import psycopg2 as pg2
import matplotlib.pyplot as plt
#only work in wsl

connection = pg2.connect(user="user", password="1234", host="localhost", port="5432", database="postgres")

def get(command):
    with connection.cursor() as cur:
        cur.execute(command)
        infos = cur.fetchall()
        #colnames = [desc[0] for desc in cur.description]
    return infos

def devs_games_quant():
    results = get("""
        SELECT count(*), num_jogos
        FROM (
            SELECT desenvolvedora.fk_Empresa_id as id_empresa, count(*) as num_jogos
            FROM desenvolvedora
            JOIN jogo ON jogo.id = desenvolvedora.fk_App_id
            GROUP BY desenvolvedora.fk_Empresa_id
        ) AS desenvolvedores_jogos
        GROUP BY num_jogos
        ORDER BY num_jogos DESC;
    """)
    x = [r[1] for r in results]
    y = [r[0] for r in results]
    
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    #ax.ylim(0, 30000)
    ax.set_xlim(0,30)
    ax.set_xlabel('Quantidade de jogos')
    ax.set_ylabel('Quantidade de desenvolvedores')
    ax.set_title("Quantidade de desenvolvedores com determinada quantidade de jogos")
    fig.savefig('data/desenvolvedores_por_quantidade_de_jogos.png')

def analises_por_ano():
    results = get("""
        SELECT 
            EXTRACT(YEAR FROM data_lancamento) AS ano, 
            AVG(analises_positivas * 100.0 / (analises_positivas + analises_negativas + 1)) AS media_analises_positivas
        FROM App
        JOIN jogo ON jogo.id = App.id
        GROUP BY ano
        ORDER BY ano;
    """)

    anos = [r[0] for r in results]
    medias_analises_positivas = [r[1] for r in results]

    fig, ax = plt.subplots(dpi=200)
    ax.plot(anos, medias_analises_positivas)
    #ax.ylim(0, 101)
    ax.set_xlim(1990,2023)
    ax.set_xlabel('Ano')
    ax.set_ylabel('Média de análises positivas (%)')
    #plt.title('Percepção da qualidade dos jogos lançados ao longo do tempo')
    ax.set_title("Média de análises positivas por ano")
    fig.savefig("data/analises_positivas_por_ano.png")

def analise_generos():
    query1 = get("""SELECT Genero.nome, AVG(App.analises_positivas * 100.0 / (App.analises_positivas + App.analises_negativas + 1)::FLOAT) as media_analises_positivas
                    FROM Genero 
                    JOIN Classificacao ON Genero.id = Classificacao.fk_Genero_id
                    JOIN App ON Classificacao.fk_App_id = App.id
                    JOIN jogo ON jogo.id = App.id
                    GROUP BY Genero.nome
                    ORDER BY media_analises_positivas DESC;""")
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]

    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)

    ax.set_xlabel('Genero')
    ax.set_ylabel('Porcentagem de análises positivas (%)')
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    plt.xticks(fontsize=4)
    ax.set_title("Porcentagem de análises positivas por genero")
    fig.savefig('data/genero_analises_positivas.png')
    
    query2 = get("""SELECT Genero.nome, COUNT(*) as quantidade_jogos
                    FROM Genero 
                    JOIN Classificacao ON Genero.id = Classificacao.fk_Genero_id
                    JOIN App ON Classificacao.fk_App_id = App.id
                    JOIN jogo ON jogo.id = App.id
                    GROUP BY Genero.nome
                    ORDER BY quantidade_jogos DESC;""")
    
    y = [r[1] for r in query2]
    x = [r[0] for r in query2]

    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Genero')
    ax.set_ylabel('Quantidade de jogos')
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    plt.xticks(fontsize=4)
    ax.set_title("Quantidade de jogos por genero")
    fig.savefig('data/genero_quant_jogos.png')
    
    query3 = get("""SELECT Genero.nome, SUM(App.analises_positivas + App.analises_negativas) as quantidade_analises
                    FROM Genero 
                    JOIN Classificacao ON Genero.id = Classificacao.fk_Genero_id
                    JOIN App ON Classificacao.fk_App_id = App.id
                    JOIN jogo ON jogo.id = App.id
                    GROUP BY Genero.nome
                    ORDER BY quantidade_analises DESC;""")
    
    y = [r[1] for r in query3]
    x = [r[0] for r in query3]

    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Genero')
    ax.set_ylabel('Quantidade de análises')
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    plt.xticks(fontsize=4)
    ax.set_title("Quantidade de análises por genero")
    fig.savefig('data/genero_quant_analises.png')

def jogos_ptrbr():
    query1 = get("""SELECT 
                date_part('year', data_lancamento) as ano,
                COUNT(DISTINCT App.id) as quantidade_jogos,
                COUNT(CASE WHEN Lingua.nome = 'Portuguese - Brazil' THEN 1 END) as quantidade_jogos_pt_br,
                100.0 * COUNT(CASE WHEN Lingua.nome = 'Portuguese - Brazil' THEN 1 END) / COUNT(DISTINCT App.id) as porcentagem_jogos_pt_br
            FROM 
                App
                LEFT JOIN Idioma ON Idioma.fk_App_id = App.id
                LEFT JOIN Lingua ON Lingua.id = Idioma.fk_Lingua_id
            	JOIN jogo ON jogo.id = App.id
            GROUP BY 
                ano
            ORDER BY 
                ano""")
    
    y = [r[2] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1990,2023)
    ax.set_ylabel('Quantidade de jogos em PT-BR')
    ax.set_title("Quantidade de jogos em PT-BR por ano")
    fig.savefig('data/pt_br_quant.png')

    y = [r[3] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_ylabel('Porcentagem de jogos em PT-BR (%)')
    ax.set_xlim(1990,2023)
    ax.set_title("Porcentagem de jogos em PT-BR por ano")
    fig.savefig('data/pt_br_porcent.png')

def analises_positivas_empresas():
    query1 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_media
        FROM (
          SELECT e.id, ROUND(AVG(a.analises_positivas::numeric / (a.analises_positivas + a.analises_negativas + 1)::numeric) * 100) AS avg_porcentagem
          FROM Empresa e
          JOIN Desenvolvedora d ON e.id = d.fk_empresa_id
          JOIN App a ON d.fk_app_id = a.id
          JOIN Jogo j ON j.id = a.id
          GROUP BY e.id
        ) subquery
        GROUP BY porcentagem_media
        ORDER BY porcentagem_media DESC;""")
    
    y = [r[0] for r in query1]
    x = [r[1] for r in query1]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinada média de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_avg.png')
    
    query2 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_maxima
        FROM (
          SELECT e.id, ROUND(MAX(a.analises_positivas::numeric / (a.analises_positivas + a.analises_negativas + 1)::numeric) * 100) AS avg_porcentagem
          FROM Empresa e
          JOIN Desenvolvedora d ON e.id = d.fk_empresa_id
          JOIN App a ON d.fk_app_id = a.id
          JOIN Jogo j ON j.id = a.id
          GROUP BY e.id
        ) subquery
        GROUP BY porcentagem_maxima
        ORDER BY porcentagem_maxima DESC;""")
    
    y = [r[0] for r in query2]
    x = [r[1] for r in query2]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinado máximo de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_max.png')
    
    query3 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_minima
        FROM (
          SELECT e.id, ROUND(MIN(a.analises_positivas::numeric / (a.analises_positivas + a.analises_negativas + 1)::numeric) * 100) AS avg_porcentagem
          FROM Empresa e
          JOIN Desenvolvedora d ON e.id = d.fk_empresa_id
          JOIN App a ON d.fk_app_id = a.id
          JOIN Jogo j ON j.id = a.id
          GROUP BY e.id
        ) subquery
        GROUP BY porcentagem_minima
        ORDER BY porcentagem_minima DESC;""")
    
    y = [r[0] for r in query3]
    x = [r[1] for r in query3]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinado mínimo de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_min.png')

def analise_dlcs_ano():
    query1 = get("""SELECT 
                    EXTRACT(YEAR FROM a.data_lancamento) AS ano_lancamento,
                    AVG(a.preco - COALESCE(dlc_total.preco_total, 0)) AS media_diff_preco_dlc
                FROM 
                    App a
                LEFT JOIN 
                    (
                        SELECT 
                            fk_Jogo_id,
                            SUM(preco) AS preco_total
                        FROM 
                            Dlc
                		JOIN app on app.id = Dlc.id
                        GROUP BY 
                            fk_Jogo_id
                    ) AS dlc_total ON dlc_total.fk_Jogo_id = a.id
                GROUP BY 
                    ano_lancamento
                ORDER BY ano_lancamento;""")
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1990,2023)
    ax.set_ylabel('Preço do jogo - preço das dlcs')
    ax.set_title("Diferença do preço de um jogo para o preço de suas Dlcs por ano")
    fig.savefig('data/dlcs_ano_dif_preco.png')

    # THE QUERY IS CONSIDERING THE YEAR THE GAME FROM THE DLC LAUNCHED (NOT ANYMORE)
    query2 = get("""SELECT 
          EXTRACT(YEAR FROM a.data_lancamento) AS ano,
          COUNT(DISTINCT a.id) AS num_jogos,
          COUNT(DISTINCT d.id) AS num_dlcs,
          COUNT(DISTINCT d.id)::FLOAT / COUNT(DISTINCT a.id)::FLOAT AS proporcao_dlcs
        FROM 
          App a
          LEFT JOIN Dlc d ON a.id = d.id
        GROUP BY 
          EXTRACT(YEAR FROM a.data_lancamento)
        ORDER BY 
          ano;""")
    

    y = [r[1] for r in query2]
    x = [r[0] for r in query2]
    fig, ax = plt.subplots(dpi=200)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1990,2023)
    ax.set_ylabel('Quantidade de dlcs')
    ax.set_title("Quantidade de dlcs por ano")
    fig.savefig('data/dlcs_ano_quant.png')


devs_games_quant()
analises_por_ano()
analise_generos()
jogos_ptrbr()
analises_positivas_empresas()
analise_dlcs_ano()