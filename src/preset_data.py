"""
Banco de dados nativo de flashcards predefinidos e organizados para:
- 14 Disciplinas do SENAI (Aprendizagem Industrial em Gestão Administrativa)
- ESAMC (Sistemas de Informação em Administração / ERP / TI)
- Cargill (Cultura, EHS / Regras de Ouro, Valores e Operações Agroindustriais)
"""

from typing import List, Dict

# ==========================================
# 1. FLASHCARDS DA CARGILL
# ==========================================
CARGILL_CARDS: List[Dict[str, str]] = [
    {
        "front": "Qual é o propósito global da <b>Cargill</b>?",
        "back": "Nutrir o mundo de forma <b>segura, responsável e sustentável</b>, conectando produtores rurais com mercados e clientes com ingredientes."
    },
    {
        "front": "Quais são os 3 <b>Valores Corporativos</b> fundamentais da Cargill?",
        "back": "<ol><li><b>Colocar as pessoas em primeiro lugar</b> (Respeito e Segurança).</li><li><b>Alcançar o sucesso juntos</b> (Colaboração e Parceria).</li><li><b>Fazer a coisa certa</b> (Integridade e Ética).</li></ol>"
    },
    {
        "front": "O que significa a autoridade de <b>Parada de Segurança (Stop Work Authority)</b> na Cargill?",
        "back": "É o direito e dever de <b>qualquer funcionário ou terceiro de interromper imediatamente</b> qualquer atividade ao identificar um risco iminente à segurança ou vida."
    },
    {
        "front": "Quais são as principais <b>Regras de Ouro de Segurança (EHS / Life Saving Rules)</b> na Cargill?",
        "back": "Práticas obrigatórias cobrindo: <b>Trabalho em Altura</b>, <b>Espaço Confinado</b>, <b>Bloqueio/Etiquetagem (LOTO)</b>, <b>Segurança de Máquinas</b> e uso adequado de <b>EPIs</b>."
    },
    {
        "front": "Qual é a estrutura de capital da Cargill no mercado global?",
        "back": "A Cargill é a <b>maior empresa privada de capital fechado dos Estados Unidos</b> (family-owned/private corporation), operando globalmente desde 1865."
    },
    {
        "front": "Como funciona a cadeia de <b>Originação de Commodities</b> da Cargill?",
        "back": "Consiste na compra direta de grãos (soja, milho, algodão) junto aos produtores rurais, oferecendo <b>barter</b>, financiamento, armazenagem em silos e transporte estratégico."
    },
    {
        "front": "O que são as <b>Boas Práticas de Fabricação (BPF / GMP)</b> nas unidades operacionais da Cargill?",
        "back": "Conjunto de procedimentos de higiene, sanitização e controle operacional para garantir a <b>segurança alimentar (Food Safety)</b> e qualidade dos produtos."
    },
    {
        "front": "Qual é o compromisso da Cargill em relação à <b>Sustentabilidade e Desmatamento Zero</b>?",
        "back": "Eliminar o desmatamento de florestas nativas em sua cadeia de suprimentos de soja e cacau, promovendo o <b>rastreamento de lotes</b> e agricultura regenerativa."
    },
    {
        "front": "O que é o sistema de <b>Barter</b> no agronegócio utilizado pela Cargill?",
        "back": "Operação financeira onde o produtor rural paga insumos (fertilizantes, defensivos, sementes) diretamente com a entrega da sua <b>safra futura de grãos</b>."
    },
    {
        "front": "Como a Cargill opera na <b>Logística Multimodal</b> de exportação no Brasil?",
        "back": "Integração de <b>rodovias, ferrovias (como a Rumo e VLI) e barcaças hidroviárias</b> para escoar grãos até portos estratégicos (Santarém, Paranaguá, Santos)."
    }
]

# ==========================================
# 2. FLASHCARDS DA ESAMC (SISTEMAS EM ADM)
# ==========================================
ESAMC_CARDS: List[Dict[str, str]] = [
    {
        "front": "O que é um sistema <b>ERP (Enterprise Resource Planning)</b> na gestão empresarial?",
        "back": "Um software integrado que unifica todas as áreas da empresa (Financeiro, Vendas, Estoque, RH, Produção) em uma <b>única base de dados centralizada</b> (ex: SAP, TOTVS)."
    },
    {
        "front": "Qual é a diferença entre um sistema <b>CRM</b> e um sistema <b>SCM</b>?",
        "back": "• <b>CRM (Customer Relationship Management)</b>: Focado na gestão de relacionamento e vendas com o cliente.<br>• <b>SCM (Supply Chain Management)</b>: Focado na gestão da cadeia de suprimentos e fornecedores."
    },
    {
        "front": "O que são <b>Sistemas de Apoio à Decisão (SAD / DSS)</b>?",
        "back": "Sistemas analíticos que combinam dados e modelos avançados para auxiliar gerentes a tomarem <b>decisões estratégicas e não estruturadas</b>."
    },
    {
        "front": "O que representa o conceito de <b>BI (Business Intelligence)</b> nas organizações?",
        "back": "Tecnologias e processos de coleta, integração e análise de dados operacionais para gerar <b>dashboards e insights estratégicos</b> de negócios."
    },
    {
        "front": "O que é um <b>Banco de Dados Relacional (RDBMS)</b> e qual a função da chave primária (PK)?",
        "back": "É um banco que organiza dados em tabelas relacionadas. A <b>Chave Primária (Primary Key)</b> identifica de forma <b>única e exclusiva</b> cada registro na tabela."
    },
    {
        "front": "O que é o protocolo de <b>Governança de TI (ex: COBIT / ITIL)</b>?",
        "back": "Conjunto de diretrizes e boas práticas para alinhar os investimentos e serviços de Tecnologia da Informação aos <b>objetivos estratégicos do negócio</b>."
    },
    {
        "front": "Qual é o papel da <b>Segurança da Informação</b> baseada no triângulo <b>CID (Confidencialidade, Integridade, Disponibilidade)</b>?",
        "back": "• <b>Confidencialidade</b>: Dados visíveis apenas a pessoas autorizadas.<br>• <b>Integridade</b>: Dados precisos sem alteração indevida.<br>• <b>Disponibilidade</b>: Sistemas acessíveis quando necessários."
    },
    {
        "front": "O que significa a integração por <b>API (Application Programming Interface)</b> nos sistemas modernos?",
        "back": "Conjunto de rotinas e padrões de programação que permite que <b>softwares diferentes troquem dados automaticamente</b> de forma segura."
    }
]

# ==========================================
# 3. FLASHCARDS DO SENAI (14 DISCIPLINAS OFICIAIS)
# ==========================================
SENAI_SUBJECTS_CARDS: Dict[str, List[Dict[str, str]]] = {
    "Fundamentos dos Processos Administrativos": [
        {
            "front": "Quais são as 4 funções fundamentais do processo administrativo (<b>PODC</b>)?",
            "back": "<b>P</b>lanejar (definir metas), <b>O</b>rganizar (alocar recursos), <b>D</b>irigir (liderar pessoas) e <b>C</b>ontrolar (avaliar resultados)."
        },
        {
            "front": "O que é um <b>Organograma</b> e qual a sua utilidade em uma empresa?",
            "back": "Gráfico representativo da <b>estrutura hierárquica</b> da organização, mostrando cargos, departamentos e linhas de autoridade/subordinação."
        },
        {
            "front": "Qual é a diferença entre um processo <b>centralizado</b> e <b>descentralizado</b>?",
            "back": "• <b>Centralizado</b>: Tomada de decisão concentrada no topo da hierarquia.<br>• <b>Descentralizado</b>: Tomada de decisão delegada aos níveis operacionais e táticos."
        }
    ],

    "Fundamentos dos Processos Financeiros": [
        {
            "front": "O que é o <b>Fluxo de Caixa (Cash Flow)</b> de uma empresa?",
            "back": "Relatório que registra todas as <b>entradas (recebimentos) e saídas (pagamentos)</b> de dinheiro em um determinado período, indicando a liquidez."
        },
        {
            "front": "Qual é a diferença entre <b>Contas a Pagar</b> e <b>Contas a Receber</b>?",
            "back": "• <b>Contas a Pagar</b>: Obrigações financeiras com fornecedores e terceiros.<br>• <b>Contas a Receber</b>: Direitos de crédito originados das vendas a clientes."
        },
        {
            "front": "O que é a <b>Conciliação Bancária</b> no setor financeiro?",
            "back": "Confronto entre o saldo do extrato bancário e os lançamentos do controle financeiro interno para garantir <b>exatidão das contas</b>."
        }
    ],

    "Fundamentos dos Processos de Gestão de Pessoas": [
        {
            "front": "Qual a diferença entre <b>Recrutamento</b> e <b>Seleção</b> de pessoal?",
            "back": "• <b>Recrutamento</b>: Atração de candidatos potenciais para a vaga.<br>• <b>Seleção</b>: Escolha e contratação do candidato mais adequado ao perfil."
        },
        {
            "front": "O que contempla o setor de <b>Departamento Pessoal (DP)</b>?",
            "back": "Rotinas burocráticas e legais trabalhistas: folha de pagamento, controle de ponto, férias, admissão, demissão e encargos sociais."
        }
    ],

    "Fundamentos de Logística": [
        {
            "front": "Qual a diferença entre os métodos de estoque <b>PEPS (FIFO)</b> e <b>UEPS (LIFO)</b>?",
            "back": "• <b>PEPS (Primeiro a Entrar, Primeiro a Sair)</b>: Produtos mais antigos são vendidos primeiro.<br>• <b>UEPS (Último a Entrar, Primeiro a Sair)</b>: Produtos mais recentes saem primeiro (proibido pelo FISCO BR para IR)."
        },
        {
            "front": "O que é a classificação de estoque pela <b>Curva ABC</b>?",
            "back": "• <b>Classe A</b>: Alta relevância financeira (80% do valor, 20% dos itens).<br>• <b>Classe B</b>: Média relevância.<br>• <b>Classe C</b>: Baixa relevância financeira (10% do valor, 50% dos itens)."
        }
    ],

    "Fundamentos da Qualidade": [
        {
            "front": "Quais são os <b>5S</b> da Metodologia de Organização e Qualidade Japonesa?",
            "back": "<ol><li><b>Seiri</b> (Utilização/Descarte)</li><li><b>Seiton</b> (Organização)</li><li><b>Seiso</b> (Limpeza)</li><li><b>Seiketsu</b> (Padronização)</li><li><b>Shitsuke</b> (Disciplina)</li></ol>"
        },
        {
            "front": "Como funciona o ciclo <b>PDCA</b> na gestão da qualidade?",
            "back": "<b>P</b>lan (Planejar), <b>D</b>o (Executar/Fazer), <b>C</b>heck (Checar/Verificar) e <b>A</b>ct (Agir corretivamente para melhoria contínua)."
        },
        {
            "front": "Para que serve o <b>Diagrama de Ishikawa (Espinha de Peixe)</b>?",
            "back": "Ferramenta visual para identificar as <b>causas-raiz</b> de um determinado problema (análise dos 6M: Mão de obra, Máquina, Material, Método, Medida, Meio ambiente)."
        }
    ],

    "Informática": [
        {
            "front": "Qual é a sintaxe e função do <b>PROCV (VLOOKUP)</b> no Excel?",
            "back": "<code>=PROCV(valor_procurado; matriz_tabela; num_indice_coluna; [procurar_intervalo])</code><br>Busca um valor na primeira coluna de uma tabela e retorna o dado correspondente."
        },
        {
            "front": "Para que serve a <b>Tabela Dinâmica</b> no Microsoft Excel?",
            "back": "Ferramenta para <b>resumir, analisar, explorar e comparar grandes volumes de dados</b> de forma rápida e flexível."
        }
    ],

    "Planejamento e Organização do Trabalho": [
        {
            "front": "Como funciona a <b>Matriz de Eisenhower</b> para gestão do tempo?",
            "back": "Divisão das tarefas em 4 quadrantes:<br>1. <b>Urgente e Importante</b>: Fazer agora.<br>2. <b>Importante, Não Urgente</b>: Agendar.<br>3. <b>Urgente, Não Importante</b>: Delegar.<br>4. <b>Não Urgente e Não Importante</b>: Eliminar."
        },
        {
            "front": "O que são metas no formato <b>SMART</b>?",
            "back": "Metas que são: <b>S</b>pecific (Específicas), <b>M</b>easurable (Mensuráveis), <b>A</b>chievable (Atingíveis), <b>R</b>elevant (Relevantes) e <b>T</b>ime-bound (Com prazo determinado)."
        }
    ],

    "Raciocínio Lógico e Análise de Dados": [
        {
            "front": "Na lógica proposicional, qual a tabela verdade da conjunção <b>'E' (&wedge;)</b>?",
            "back": "A proposição composta só é <b>VERDADEIRA</b> se <b>ambas as proposições simples forem verdadeiras</b>."
        },
        {
            "front": "Qual a diferença entre <b>Média, Mediana e Moda</b> na análise estatística?",
            "back": "• <b>Média</b>: Soma dos valores dividida pela quantidade.<br>• <b>Mediana</b>: Valor central de um conjunto ordenado.<br>• <b>Moda</b>: Valor que aparece com maior frequência."
        }
    ],

    "Transformação Digital no Setor Industrial": [
        {
            "front": "O que caracteriza a <b>Indústria 4.0 (Quarta Revolução Industrial)</b>?",
            "back": "Integração de sistemas físicos e virtuais por meio de <b>IoT (Internet das Coisas)</b>, Inteligência Artificial, Big Data, Computação em Nuvem e Robótica Avançada."
        },
        {
            "front": "O que representa a sigla <b>IoT (Internet of Things / Internet das Coisas)</b> na fábrica?",
            "back": "Rede de sensores e dispositivos físicos conectados que <b>coletam e trocam dados em tempo real</b> para monitoramento preditivo de máquinas."
        }
    ],

    "Saúde e Segurança do Trabalho": [
        {
            "front": "Qual a diferença entre <b>EPI</b> e <b>EPC</b> na segurança do trabalho?",
            "back": "• <b>EPI (Equipamento de Proteção Individual)</b>: Protege um único trabalhador (ex: capacete, óculos, protetor auricular).<br>• <b>EPC (Equipamento de Proteção Coletiva)</b>: Protege o ambiente e todos os trabalhadores (ex: exaustores, guarda-corpo, fiação isolada)."
        },
        {
            "front": "O que é a <b>CIPA (Comissão Interna de Prevenção de Acidentes e Assédio)</b>?",
            "back": "Comissão formada por representantes dos empregados e do empregador para <b>prevenir acidentes, promover a saúde e combater o assédio no trabalho</b>."
        }
    ],

    "Fundamentos da Leitura de Desenhos Técnicos e Metrologia": [
        {
            "front": "Quais são as 3 <b>vistas ortogonais principais</b> de um desenho técnico no 1º diedro?",
            "back": "1. <b>Vista Frontal</b> (Principal)<br>2. <b>Vista Superior</b> (Vista de cima)<br>3. <b>Vista Lateral Esquerda</b> (Posicionada à direita no desenho)."
        },
        {
            "front": "Qual é a função do instrumento de medição chamado <b>Paquímetro</b>?",
            "back": "Instrumento de alta precisão usado para medir <b>dimensões internas, externas, profundidade e ressaltos</b> de peças."
        }
    ],

    "Práticas Inovadoras": [
        {
            "front": "O que é a metodologia de resolução de problemas chamada <b>Design Thinking</b>?",
            "back": "Abordagem focada no ser humano dividida em 5 fases: <b>Empatizar, Definir, Idear, Prototipar e Testar</b>."
        },
        {
            "front": "O que é o quadro visual <b>Kanban</b> em metodologias ágeis?",
            "back": "Ferramenta de gestão de fluxo de trabalho visual dividida em colunas simples como: <b>A Fazer (To Do), Em Andamento (Doing) e Concluído (Done)</b>."
        }
    ],

    "Fundamentos da Comunicação e Informação": [
        {
            "front": "Quais são as características da linguagem em uma <b>Redação Oficial / Documentação Técnica</b>?",
            "back": "<b>Clareza, concisão, impessoalidade, formalidade</b> e obediência à norma-padrão da língua portuguesa."
        },
        {
            "front": "O que é o <b>Memorando</b> no ambiente corporativo tradicional?",
            "back": "Comunicação escrita <b>interna e agilizada</b> entre setores/departamentos da mesma empresa."
        }
    ],

    "Relações Socioprofissionais, Cidadania e Ética": [
        {
            "front": "Qual a diferença entre <b>Ética</b> e <b>Moral</b>?",
            "back": "• <b>Moral</b>: Conjunto de regras, costumes e valores de uma cultura ou sociedade específica.<br>• <b>Ética</b>: Reflexão filosófica e crítica sobre os princípios que fundamentam a moral."
        },
        {
            "front": "O que são os <b>Direitos do Aprendiz</b> pela Lei nº 10.097/2000 (Lei da Aprendizagem)?",
            "back": "Registro em CTPS, salário mínimo hora, jornada de no máximo 6h ou 8h, recolhimento de <b>2% de FGTS</b>, férias coincidentes com recesso escolar e curso teórico no SENAI."
        }
    ]
}

def get_all_senai_cards_flat() -> List[Dict[str, str]]:
    """Retorna a lista completa de todos os cards do SENAI concatenados."""
    all_cards = []
    for subject, cards in SENAI_SUBJECTS_CARDS.items():
        for c in cards:
            all_cards.append({
                "front": f"<small style='color:#89b4fa;'>[SENAI - {subject}]</small><br>{c['front']}",
                "back": c["back"]
            })
    return all_cards
