    st.write("df_channels_sample : ")

    st.dataframe(df_channels_sample)
    import os
    st.write("OS write  : ")
    os.write(1,b'some text @@@@@@ $$$$$ %%%%%%')
    os.write(1,df_channels_sample.to_string().encode('utf-8'))



- When proposing an edit to a markdown file, first decide if there will be code snippets in the markdown file.
- If there are no code snippets, wrap the beginning and end of your answer in backticks and markdown as the language.
- If there are code snippets, indent the code snippets with two spaces and the correct language for proper rendering. Indentations level 0 and 4 is not allowed.
- If a markdown code block is indented with any value other than 2 spaces, automatically fix it





consider st.plotly_chart(
    fig,
    use_container_width=True,
    config={"staticPlot": True}   # <- makes it behave like a PNG
)
staticPlot: True removes the JS bundle and interactivity; good for large scatter charts where hover & zoom are not essential.



5. .clear() and manual GC
load_daily_data.clear()
Every function wrapped by a Streamlit cache decorator gains a .clear() method. Calling it invalidates its stored value immediately—handy if you push new Parquet files and want the container to reload them without waiting for tomorrow.

Manual gc.collect() button
Purely a debugging aid. If you suspect a leak, insert it, click it a few times while watching Cloud-Run memory graphs. Once you’re happy, remove it.


cat /etc/debian_version
cat /etc/os-release

$ cat /etc/debian_version
12.10

 $ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
NAME="Debian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"

find /usr -name "index.html"

https://creatorsengine.com.br/timeout
https://discuss.streamlit.io/t/how-to-configure-an-idle-timeout-for-a-streamlit-app-deployed-on-gcp-cloud-run/89252


to rebuild : docker compose -f 'docker-compose.yml' up -d --build 'dev'
docker tag ce_applab-dev:latest streamlit-filter-ui-dev:latest


streamlit run main.py --server.port=8080 --server.address=0.0.0.0

 $ sips -s format jpeg -s formatOptions 100 --padColor FFFFFF -o foo.jpg ./foo.png

https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1#google.cloud.vision.v1.SafeSearchAnnotation
https://cloud.google.com/vision/docs/reference/rpc/google.cloud.vision.v1#google.cloud.vision.v1.Likelihood


Campos
adulto
Probabilidade

Representa a probabilidade de conteúdo adulto para a imagem. Conteúdo adulto pode conter elementos como nudez, imagens ou desenhos pornográficos, ou atividades sexuais.

spoof
Probabilidade

Probabilidade de paródia. A probabilidade de que uma modificação tenha sido feita na versão canônica da imagem para torná-la engraçada ou ofensiva.

médico
Probabilidade

Probabilidade de que esta seja uma imagem médica.

violência
Probabilidade

Probabilidade de que esta imagem contenha conteúdo violento. Conteúdo violento pode incluir morte, danos graves ou ferimentos a indivíduos ou grupos de indivíduos.

picante
Probabilidade

Probabilidade de que a imagem solicitada contenha conteúdo picante. Conteúdo picante pode incluir (mas não se limita a) roupas curtas ou transparentes, nudez estrategicamente coberta, poses obscenas ou provocativas ou closes de áreas sensíveis do corpo.


# MDM Vision AI App

## Descrição
Aplicativo Streamlit para análise de imagens (miniaturas do YouTube) usando Google Cloud Vision AI. O app oferece uma interface simplificada para upload de imagens, processamento com Vision AI e visualização dos resultados.

## Funcionalidades Principais
- Análise de imagens usando Google Cloud Vision AI:
  - Detecção de conteúdo explícito (SafeSearch)
  - Detecção de Labels
- Interface em Português Brasileiro
- Suporte a múltiplas fontes de imagem:
  - Upload de arquivo
  - URL da imagem
  - ID ou URL do YouTube
- Cache de resultados para evitar reprocessamento
- Visualização prévia da imagem antes do processamento

## Estrutura do Projeto
```
/mdm_app (pasta raiz)
├── components/
│   ├── navigation.py     # Componentes de navegação UI
│   ├── tables.py         # Componentes de renderização de tabelas
│   ├── forms.py          # Componentes de formulários
│   └── messaging.py      # Mensagens de sucesso/erro
├── img/
│   ├── mdm_logo.png      # Logo do Cliente (PNG com Alpha)
│   ├── home_mdm.jpg      # Imagem da página inicial
│   └── app_logo.jpg      # Logo do app
├── pages/
│   ├── home.py           # Página inicial
│   ├── creators_engine_ia.py      # Página Creators Engine IA
│   └── feedback.py       # Página de Feedback
├── utils/
│   ├── validation.py     # Funções de validação
│   ├── auth.py          # Utilitários de autenticação
│   └── config.py        # Variáveis compartilhadas e configurações
├── main.py              # Ponto de entrada
└── README.md            # Este arquivo
```

## Requisitos Técnicos
- Python 3.11
- Pacotes principais:
  - streamlit
  - google-cloud-vision
  - google-cloud-storage
  - requests

## Autenticação
- Autenticação principal via GCP Identity-Aware Proxy
- Autenticação de fallback com senha simples
- Sessão mantida durante todo o uso

## Páginas
1. **Home**
   - Página de boas-vindas com texto introdutório
   - Exibição do logo do cliente

2. **Vision AI**
   - Upload/entrada de imagens
   - Visualização prévia
   - Resultados SafeSearch com código de cores
   - Tabela de Labels detectados
   - Cache de resultados processados

3. **Feedback**
   - Texto informativo
   - Email para contato

## Princípios de Design
- Interface minimalista usando componentes padrão Streamlit
- Layout wide com sidebar expandida
- Sem CSS customizado ou formatação complexa
- Foco na funcionalidade e usabilidade

## Tratamento de Erros
- Falha graciosa com mensagens de erro claras
- Logging simplificado via print()
- Validação de entradas de usuário

## Armazenamento
- Resultados salvos no Google Cloud Storage @ yta_mdm_production/creators-engine-vision
- Cache local para evitar reprocessamento
- Sem uso de banco de dados

## Notas de Desenvolvimento
- Manter arquivos Python com menos de 200 linhas
- Comentários de histórico no topo dos arquivos
- Código modular e reutilizável
- Princípio DRY (Don't Repeat Yourself)