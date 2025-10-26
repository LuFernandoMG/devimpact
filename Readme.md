# DevImpact - Assistente de Benefícios Sociais

Este projeto é um assistente telefônico inteligente que ajuda pessoas a descobrir quais benefícios sociais do governo de São Paulo elas podem ter acesso. O sistema utiliza GPT-4o Realtime, guardrails de moderación, e RAG (Retrieval Augmented Generation) para fornecer informações precisas e relevantes.

## 🏗️ Estrutura do Projeto

O projeto possui duas versões diferentes:

1. **Versão Base (Web Local)**: Interface web que permite conversar com o assistente via navegador
2. **Versão Twilio**: Integração com Twilio para chamadas telefônicas reais

```
devimpact/
├── app/
│   ├── base_version/          # Versão web local
│   │   ├── main.py            # Aplicação Flask principal
│   │   ├── static/            # Arquivos estáticos (HTML)
│   │   ├── utils/             # Utilitários (guardrails, RAG)
│   │   └── chroma_db/         # Base de dados local (opcional)
│   │
│   └── twilios_version/      # Versão Twilio
│       ├── app.py             # Aplicação Flask + WebSockets
│       ├── openai_realtime.py # Cliente Realtime API
│       ├── guardrails.py      # Sistema de moderación
│       ├── rag.py             # Sistema RAG
│       └── data/              # Base de conocimiento JSONL
├── requirements.txt           # Dependências Python
├── dockerfile                # Container Docker para Twilio
└── README.md
```

## 🚀 Configuração Inicial

### Pré-requisitos

- Python 3.11+
- OpenAI API Key
- (Opcional) ngrok para exposição pública
- (Opcional) Conta Twilio para versão telefônica

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto ou configure as variáveis:

```bash
export OPENAI_API_KEY="sk-..."
```

## 📱 Versão 1: Web Local (Browser)

Esta versão cria uma interface web que permite conversar com o assistente diretamente no navegador.

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

### Execução Local

```bash
# Navegar para a versão base
cd app/base_version

# Executar a aplicação
python main.py
```

A aplicação estará disponível em: `http://localhost:8080`

### Funcionalidades

- ✅ Interface web interativa com botão "Iniciar conversación"
- ✅ Comunicação em tempo real com GPT-4o
- ✅ Guardrails para moderación de conteúdo
- ✅ Sistema RAG para busca de benefícios sociais
- ✅ Suporte a WebRTC para áudio bidireccional

### Endpoints

- `GET /`: Interface web principal
- `GET /session`: Gera sessão Realtime para o navegador
- `POST /analyze`: Analisa entrada do usuário e retorna benefícios sugeridos

## 📞 Versão 2: Twilio (Phone)

Esta versão integra com Twilio para permitir chamadas telefônicas reais.

### Instalação

```bash
# Instalar dependências (mesmo arquivo requirements.txt)
pip install -r requirements.txt
```

### Execução com Docker

```bash
# Construir a imagem
docker build -t devimpact-twilio .

# Executar o container
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="sk-..." \
  -e REALTIME_MODEL="gpt-4o-mini-realtime-preview" \
  -e REALTIME_VOICE="alloy" \
  -e LANGUAGE="pt" \
  devimpact-twilio
```

### Execução Local (Sem Docker)

```bash
cd app/twilios_version

# Definir variáveis de ambiente
export OPENAI_API_KEY="sk-..."
export REALTIME_MODEL="gpt-4o-mini-realtime-preview"
export REALTIME_VOICE="alloy"
export LANGUAGE="pt"

# Executar com gunicorn
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
  -w 1 -b 0.0.0.0:8080 app:app
```

### Configuração Twilio

1. **Configurar ngrok** para exponer o servidor local:
```bash
ngrok http 8080
```

2. **No Console Twilio**, configurar:
   - **Webhook URL**: `https://SEU-DOMINIO-NGROK/incoming-call`
   - **Method**: POST

3. **Webhook Events**: Habilitar "Status Callback"

### Endpoints

- `GET /`: Status da API
- `GET /health`: Health check
- `POST /incoming-call`: Endpoint chamado pelo Twilio quando há chamada recebida
- `WS /twilio-media`: WebSocket para streaming bidireccional de áudio

### Fluxo de Uma Chamada

1. Usuário liga para número Twilio
2. Twilio POST para `/incoming-call` → retorna TwiML com `<Stream>`
3. Twilio conecta WebSocket para `/twilio-media`
4. Servidor:
   - Conecta ao OpenAI Realtime API
   - Faz transcrição de entrada do usuário
   - Aplica guardrails (moderación)
   - Busca contexto relevante via RAG
   - Injeta contexto como system prompt
   - Cria resposta de áudio
   - Stream de áudio para Twilio → usuário ouve resposta

## 🛡️ Segurança e Moderación

Ambas as versões incluem:

- **Guardrails**: Moderación automática usando OpenAI Moderation API
- **RAG**: Sistema de recuperação de contexto para fornecer informações precisas
- **Validação de entrada**: Filtros contra conteúdo inapropiado

## 🧪 Teste Local

### Testar Versão Base (Web)

```bash
cd app/base_version
export OPENAI_API_KEY="sk-..."
python main.py
# Abrir navegador em http://localhost:8080
```

### Testar Versão Twilio

```bash
cd app/twilios_version
export OPENAI_API_KEY="sk-..."
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:8080 app:app

# Em outro terminal:
ngrok http 8080
# Configurar URL do ngrok no Twilio Console
```

## 📦 Deploy

### Deploy com Docker

```bash
# Build
docker build -t devimpact-twilio .

# Run
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  devimpact-twilio
```

### Deploy para Cloud (ex: Google Cloud Run)

```bash
# Construir e enviar para Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/devimpact

# Deploy no Cloud Run
gcloud run deploy devimpact \
  --image gcr.io/PROJECT_ID/devimpact \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

## 🔧 Troubleshooting

### Erro: "Invalid HTTP method"
Normal quando WebSocket tenta conexão antes de ser aceita pelo servidor gevent. Isso é esperado e não afeta o funcionamento.

### Erro: "Falta OPENAI_API_KEY"
Certifique-se de que a variável de ambiente está configurada:
```bash
export OPENAI_API_KEY="sk-..."
```

### Twilio não conecta
1. Verifique que ngrok está rodando e é acessível publicamente
2. Certifique-se que a URL do webhook no Twilio está correta
3. Verifique logs do servidor para erros de conexão

## 📝 Licença

Este projeto é fornecido como está para fins educacionais e de demonstração.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

