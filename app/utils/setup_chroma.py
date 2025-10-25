import chromadb
import os

COLLECTION_NAME = "beneficios_sp"
DB_PATH = "./chroma_db"
os.makedirs(DB_PATH, exist_ok=True)

# Cliente do ChromaDB
client = chromadb.PersistentClient(path=DB_PATH)

try:
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        print(f"Coleção '{COLLECTION_NAME}' já existe. Removendo para recriar...")
        client.delete_collection(name=COLLECTION_NAME)
except Exception as e:
    print(f"Erro ao tentar deletar coleção: {e}")

collection = client.create_collection(name=COLLECTION_NAME)

collection.add(
    documents=[
        # CadÚnico
        "O Cadastro Único, ou CadÚnico, é a porta de entrada para programas sociais do Governo Federal. "
        "Podem se cadastrar famílias com renda mensal de até meio salário-mínimo por pessoa, ou seja, "
        "cerca de 706 reais por pessoa. Também podem se cadastrar famílias com renda total de até 3 salários-mínimos. "
        "Pessoas que moram sozinhas também podem se inscrever. O cadastro é feito no CRAS, "
        "o Centro de Referência de Assistência Social, da sua cidade. É preciso levar CPF ou Título de Eleitor "
        "do responsável pela família e documentos de todos que moram na casa.",

        # Bolsa Trabalho
        "O Bolsa Trabalho é um programa do governo de São Paulo, parte do Bolsa do Povo. "
        "É voltado para pessoas desempregadas há mais de um ano e que não estão recebendo seguro-desemprego. "
        "O participante precisa ter 18 anos ou mais, morar no estado de São Paulo e ter uma renda familiar "
        "por pessoa de até meio salário-mínimo. O benefício é uma bolsa de 540 reais por mês, "
        "por até cinco meses. Em troca, a pessoa presta serviços em órgãos públicos e faz um curso de qualificação.",

        # Ação Jovem
        "O Ação Jovem é um programa do Bolsa do Povo, do governo de São Paulo. "
        "O objetivo é ajudar jovens de 15 a 24 anos a terminarem os estudos (ensino fundamental ou médio). "
        "Para participar, o jovem precisa estar matriculado na escola (regular ou EJA) e ter uma renda familiar "
        "por pessoa de até meio salário-mínimo. O programa paga um auxílio de 100 reais por mês. "
        "É obrigatório ter pelo menos 75% de frequência nas aulas e participar de atividades complementares.",

        # Renda Cidadã
        "O Renda Cidadã é um programa estadual de São Paulo para famílias em situação de grande vulnerabilidade social. "
        "Ele atende famílias que estão passando por muitas dificuldades, dando prioridade para aquelas chefiadas "
        "por mulheres, com crianças pequenas de até 6 anos, e com a menor renda. "
        "O programa paga um auxílio mensal, que é de 100 reais, para ajudar no sustento da família. "
        "A família precisa estar inscrita no CadÚnico e ser acompanhada pelo CRAS.",
        
        # BPC (Benefício de Prestação Continuada) - Bônus, muito buscado
        "O BPC, Benefício de Prestação Continuada, é um benefício do Governo Federal no valor de um salário-mínimo por mês. "
        "Ele é destinado a idosos com 65 anos ou mais e pessoas com deficiência de qualquer idade (física, mental, "
        "intelectual ou sensorial) que não podem trabalhar. Nos dois casos, a renda por pessoa da família "
        "deve ser menor que um quarto do salário-mínimo. Não é preciso ter contribuído para o INSS para receber. "
        "É necessário estar inscrito no CadÚnico."
    ],
    metadatas=[
        {"programa": "Cadastro Único (CadÚnico)"},
        {"programa": "Bolsa Trabalho (Bolsa do Povo)"},
        {"programa": "Ação Jovem (Bolsa do Povo)"},
        {"programa": "Renda Cidadã (Bolsa do Povo)"},
        {"programa": "Benefício de Prestação Continuada (BPC)"}
    ],
    ids=[
        "cadunico_001",
        "bolsa_trabalho_001",
        "acao_jovem_001",
        "renda_cidada_001",
        "bpc_001"
    ]
)

print(f"Banco de dados populado com sucesso.")
print(f"Total de documentos na coleção '{COLLECTION_NAME}': {collection.count()}")