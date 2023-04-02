import psycopg2 as pg2
import matplotlib.pyplot as plt

connection = pg2.connect(user="user", password="1234", host="localhost", port="5432", database="postgres")

def get(command):
    with connection.cursor() as cur:
        cur.execute(command)
        infos = cur.fetchall()
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
    
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlim(0,30)
    ax.set_xlabel('Quantidade de jogos')
    ax.set_ylabel('Quantidade de desenvolvedores')
    ax.set_title("Quantidade de desenvolvedores com determinada quantidade de jogos")
    fig.savefig('data/desenvolvedores_por_quantidade_de_jogos.png')

def analises_por_ano():
    results = get("""
        SELECT 
            EXTRACT(YEAR FROM data_lancamento) AS ano, 
            AVG(analises_positivas * 100.0 / NULLIF(analises_positivas + analises_negativas, 0)) AS media_analises_positivas
        FROM App
        JOIN jogo ON jogo.id = App.id
        GROUP BY ano
        ORDER BY ano;
    """)

    anos = [r[0] for r in results]
    medias_analises_positivas = [r[1] for r in results]

    fig, ax = plt.subplots(dpi=300)
    ax.plot(anos, medias_analises_positivas)
    ax.set_xlim(1997,2023)
    ax.set_xlabel('Ano')
    ax.set_ylabel('Média de análises positivas (%)')
    ax.set_title("Média de análises positivas por ano")
    fig.savefig("data/analises_positivas_por_ano.png")

def analise_generos():
    query1 = get("""SELECT Genero.nome, AVG(App.analises_positivas * 100.0 / NULLIF((App.analises_positivas + App.analises_negativas)::FLOAT,0)) as media_analises_positivas
                    FROM Genero 
                    JOIN Classificacao ON Genero.id = Classificacao.fk_Genero_id
                    JOIN App ON Classificacao.fk_App_id = App.id
                    JOIN jogo ON jogo.id = App.id
                    GROUP BY Genero.nome
                    ORDER BY media_analises_positivas DESC;""")
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]

    fig, ax = plt.subplots(dpi=300)
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

    fig, ax = plt.subplots(dpi=300)
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

    fig, ax = plt.subplots(dpi=300)
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
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Quantidade de jogos em PT-BR')
    ax.set_title("Quantidade de jogos em PT-BR por ano")
    fig.savefig('data/pt_br_quant.png')

    y = [r[2] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_ylabel('Porcentagem de jogos em PT-BR (%)')
    ax.set_xlim(1997,2023)
    ax.set_title("Porcentagem de jogos em PT-BR por ano")
    fig.savefig('data/pt_br_porcent.png')

def analises_positivas_empresas():
    query1 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_media
        FROM (
          SELECT e.id, ROUND(AVG(a.analises_positivas::numeric / NULLIF((a.analises_positivas + a.analises_negativas)::numeric, 0)) * 100) AS avg_porcentagem
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
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinada média de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_avg.png')
    
    query2 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_maxima
        FROM (
          SELECT e.id, ROUND(MAX(a.analises_positivas::numeric / NULLIF((a.analises_positivas + a.analises_negativas)::numeric,0)) * 100) AS avg_porcentagem
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
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinado máximo de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_max.png')
    
    query3 = get("""SELECT COUNT(*) AS quantidade_empresas, ROUND(avg_porcentagem) AS porcentagem_minima
        FROM (
          SELECT e.id, ROUND(MIN(a.analises_positivas::numeric / NULLIF((a.analises_positivas + a.analises_negativas)::numeric, 0)) * 100) AS avg_porcentagem
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
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem de análises positivas (%)')
    ax.set_ylabel('Quantidade de empresas')
    ax.set_title("Quantidade de empresas com determinado mínimo de porcentagem de análises positivas", size=10)
    fig.savefig('data/empresa_porcent_min.png')

def analise_dlcs_ano():
    query1 = get("""SELECT 
                    EXTRACT(YEAR FROM a.data_lancamento) AS ano_lancamento,
                    AVG(a.preco - COALESCE(dlc_total.preco_total, 0)) AS media_diff_preco_dlc
                FROM App a
                JOIN Jogo j ON j.id = a.id
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
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Preço do jogo - preço das dlcs')
    ax.set_title("Diferença do preço de um jogo para o preço de suas Dlcs por ano")
    fig.savefig('data/dlcs_ano_dif_preco.png')

    query2 = get("""SELECT 
          EXTRACT(YEAR FROM a.data_lancamento) AS ano,
          COUNT(DISTINCT d.id)::FLOAT / COUNT(DISTINCT a.id)::FLOAT*100 AS proporcao_dlcs
        FROM 
          App a
          LEFT JOIN Dlc d ON a.id = d.id
        GROUP BY 
          EXTRACT(YEAR FROM a.data_lancamento)
        ORDER BY 
          ano;""")
    

    y = [r[1] for r in query2]
    x = [r[0] for r in query2]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Porcentagem de dlcs')
    ax.set_title("Porcentagem de dlcs por ano")
    fig.savefig('data/dlcs_ano_quant.png')

def tags_mais_populares():
    query1 = get("""SELECT t.nome AS tag, SUM(a.analises_positivas + a.analises_negativas) AS total_analises
            FROM (
                SELECT fk_App_id, fk_Tag_id, quantidade,
                ROW_NUMBER() OVER (PARTITION BY fk_App_id ORDER BY quantidade DESC) AS tag_rank
                FROM Tags
            ) AS t1
            INNER JOIN Tag AS t ON t.id = t1.fk_Tag_id
            INNER JOIN App AS a ON a.id = t1.fk_App_id
            INNER JOIN JOGO AS j ON j.id = a.id
            WHERE t1.tag_rank <= 4
            GROUP BY t.nome
            ORDER BY total_analises DESC
            LIMIT 20;""")
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    plt.xticks(fontsize=4)
    ax.set_xlabel('Tags')
    ax.set_ylabel('Quantidade de análises')
    ax.set_title("Quantidade de análises por tag (20 mais populares)")
    fig.savefig('data/quant_analises_tags_20.png')

    query2 = get("""SELECT t.nome AS tag, COUNT(DISTINCT a.id) AS quant_jogos
            FROM (
                SELECT fk_App_id, fk_Tag_id, quantidade,
                ROW_NUMBER() OVER (PARTITION BY fk_App_id ORDER BY quantidade DESC) AS tag_rank
                FROM Tags
            ) AS t1
            INNER JOIN Tag AS t ON t.id = t1.fk_Tag_id
            INNER JOIN App AS a ON a.id = t1.fk_App_id
            INNER JOIN JOGO AS j ON j.id = a.id
            WHERE t1.tag_rank <= 4
            GROUP BY t.nome
            ORDER BY quant_jogos DESC
            LIMIT 20;""")
    

    y = [r[1] for r in query2]
    x = [r[0] for r in query2]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')
    plt.xticks(fontsize=4)
    ax.set_xlabel('Tags')
    ax.set_ylabel('Quantidade de jogos')
    ax.set_title("Quantidade de jogos por tag (20 mais populares)")
    fig.savefig('data/quant_jogos_tags_20.png')

def acessibilidade():
    query1 = get("""SELECT
            EXTRACT(YEAR FROM data_lancamento) AS ano,
            ROUND(CAST(COUNT(DISTINCT CASE WHEN categorias.nome IN 
            				 ('Partial Controller Support',
            				  'Full controller support') THEN app.id ELSE NULL END) AS NUMERIC) / COUNT(DISTINCT app.id) * 100, 2) AS porcentagem_controle
            FROM
            App app
            JOIN Jogo j ON j.id=app.id
            LEFT JOIN Categorizacao categorizacao ON app.id = categorizacao.fk_App_id
            LEFT JOIN Categoria categorias ON categorizacao.fk_Categoria_id = categorias.id
            GROUP BY
            ano
            ORDER BY
            ano ASC;""")
    
    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Porcentagem de jogos com suporte para controle (%)')
    ax.set_title("Porcentagem de jogos com suporte para controle por ano")
    fig.savefig('data/jogos_controle_ano.png')

    query2 = get("""SELECT 
                EXTRACT(YEAR FROM data_lancamento) AS ano_lancamento,
                ROUND(AVG(preco), 2) AS preco_medio
            FROM 
                App
                INNER JOIN Jogo ON Jogo.id = App.id
            GROUP BY 
                ano_lancamento
            ORDER BY 
                ano_lancamento;
            """)
    
    y = [r[1] for r in query2]
    x = [r[0] for r in query2]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Preço médio de jogos')
    ax.set_title("Preço médio de jogos por ano")
    fig.savefig('data/jogos_preco_ano.png')

    query3 = get("""SELECT 
                EXTRACT(YEAR FROM data_lancamento) AS ano_lancamento,
                ROUND(COUNT(CASE WHEN linux_support OR mac_support THEN 1 END) * 100.0 / COUNT(*), 2) AS porcentagem_suporte
            FROM 
                App
                INNER JOIN Jogo ON Jogo.id = App.id
            GROUP BY 
                ano_lancamento
            ORDER BY 
                ano_lancamento;
            """)
    
    y = [r[1] for r in query3]
    x = [r[0] for r in query3]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Suporte para mac/linux (%)')
    ax.set_title("Suporte para mac/linux por ano")
    fig.savefig('data/jogos_mac_linux_ano.png')

    query4 = get("""SELECT EXTRACT(YEAR FROM a.data_lancamento) AS ano,
                AVG((SELECT COUNT(*) FROM Idioma WHERE fk_App_id = a.id)) AS media_idiomas
            FROM App AS a
            INNER JOIN Jogo AS j ON j.id = a.id
            GROUP BY ano
            ORDER BY ano ASC;
            """)
    
    y = [r[1] for r in query4]
    x = [r[0] for r in query4]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Média de idioma de jogos')
    ax.set_title("Média de idioma de jogos por ano")
    fig.savefig('data/jogos_idioma_ano.png')

def singleplayer_multiplayer():
    query1 = get("""
        SELECT 
        EXTRACT(year FROM data_lancamento) AS ano, 
        ROUND(COUNT(DISTINCT CASE WHEN Categoria.nome  
    				IN ('Single-player')
    				THEN App.id END) * 100.0 / COUNT(DISTINCT App.id), 2) AS perc_singleplayer
    FROM 
        App 
    	INNER JOIN jogo j on j.id=App.id
        INNER JOIN Categorizacao ON App.id = Categorizacao.fk_App_id 
        INNER JOIN Categoria ON Categoria.id = Categorizacao.fk_Categoria_id
    GROUP BY 
        ano
    ORDER BY 
        ano;
    """)

    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y, label="Single-player")

    #multi count
    query2 = get("""
            SELECT 
            EXTRACT(year FROM data_lancamento) AS ano, 
            ROUND(COUNT(DISTINCT CASE WHEN Categoria.nome  
        				IN ('Multi-player')
        				THEN App.id END) * 100.0 / COUNT(DISTINCT App.id), 2) AS perc_multiplayer
        FROM 
            App 
        	INNER JOIN jogo j on j.id=App.id
            INNER JOIN Categorizacao ON App.id = Categorizacao.fk_App_id 
            INNER JOIN Categoria ON Categoria.id = Categorizacao.fk_Categoria_id
        GROUP BY 
            ano
        ORDER BY 
            ano;
    """)
    y = [r[1] for r in query2]
    x = [r[0] for r in query2]
    ax.plot(x, y, label="Multi-player")
    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Porcentagem de jogos (%)')
    ax.set_title("Porcentagem de jogos por ano")
    ax.legend()
    fig.savefig('data/single_multi_percent_ano.png')

    query3 = get("""
    SELECT EXTRACT(year FROM data_lancamento) as ano, SUM(CASE WHEN Categoria.nome  IN ('Single-player')
    THEN app.analises_positivas + app.analises_negativas ELSE 0 END) as analises_tot FROM APP
    JOIN jogo on jogo.id = app.id
    INNER JOIN Categorizacao ON App.id = Categorizacao.fk_App_id 
    INNER JOIN Categoria ON Categoria.id = Categorizacao.fk_Categoria_id
    GROUP BY ano
    ORDER BY ANO
    """)
    y = [r[1] for r in query3]
    x = [r[0] for r in query3]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y, label="Single-player")

    query4 = get("""
    SELECT EXTRACT(year FROM data_lancamento) as ano, SUM(CASE WHEN Categoria.nome  IN ('Multi-player')
    THEN app.analises_positivas + app.analises_negativas ELSE 0 END) as analises_tot FROM APP
    JOIN jogo on jogo.id = app.id
    INNER JOIN Categorizacao ON App.id = Categorizacao.fk_App_id 
    INNER JOIN Categoria ON Categoria.id = Categorizacao.fk_Categoria_id
    GROUP BY ano
    ORDER BY ANO
    """)
    y = [r[1] for r in query4]
    x = [r[0] for r in query4]
    ax.plot(x, y, label="Multi-player")

    ax.set_xlabel('Ano')
    ax.set_xlim(1997,2023)
    ax.set_ylabel('Quantidade de análises de jogos')
    ax.set_title("Quantidade de análises por ano")
    ax.legend()
    fig.savefig('data/single_multi_quant_ano.png')

def preco_mais_populares():
    query1 = get("""
    WITH jogos_populares AS (
        SELECT 
            App.id, 
            preco, 
            NTILE(100) OVER (ORDER BY analises_positivas + analises_negativas DESC) AS conj
        FROM App
        JOIN JOGO j on j.id=App.id
    )
    SELECT 
        t.conj,
        (SELECT ROUND(AVG(preco)::NUMERIC, 2) AS media_preco
            FROM jogos_populares
            WHERE  jogos_populares.conj <= t.conj
        ) AS media_preco
    FROM
    (SELECT DISTINCT conj FROM jogos_populares) AS t
    ORDER BY t.conj ASC;
    """)

    y = [r[1] for r in query1]
    x = [r[0] for r in query1]
    fig, ax = plt.subplots(dpi=300)
    ax.plot(x, y)
    ax.set_xlabel('Porcentagem dos jogos mais populares (%)')
    ax.set_ylabel('Média de preço dos jogos')
    ax.set_title("Média de preço para os jogos mais populares")
    fig.savefig('data/jogos_populares_media.png')

devs_games_quant()
analises_por_ano()
analise_generos()
jogos_ptrbr()
analises_positivas_empresas()
analise_dlcs_ano()
tags_mais_populares()
acessibilidade()
singleplayer_multiplayer()
preco_mais_populares()