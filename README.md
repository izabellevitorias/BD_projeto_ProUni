# Dashboard ProUni

Dashboard interativo para análise de dados do Programa Universidade para Todos (ProUni), desenvolvido com Streamlit e MongoDB.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

* Git
* Docker Desktop (recomendado)
* Docker Compose
---

## Clonando o Projeto

Clone o repositório:

```bash
git clone https://github.com/izabellevitorias/BD_projeto_ProUni.git
```

Acesse a pasta da aplicação:

```bash
cd BD_projeto_ProUni/app
```

---

## Configuração do Ambiente

Crie um arquivo `.env` na pasta `app`:

```bash
cat > .env << 'EOF'
MONGODB_URI='mongodb+srv://SEU_USUARIO:SUA_SENHA@cluster.mongodb.net/?retryWrites=true&w=majority'
MONGODB_DB='proUni'
MONGODB_COLLECTION='dados2020'
EOF
```

> Caso já possua um arquivo `.env`, basta copiá-lo para a pasta `app`.

---

## Executando com Docker (Recomendado)

Na pasta `app`, execute:

```bash
docker compose up --build
```

Após a inicialização, acesse:

```text
http://localhost:8501
```

Para encerrar a aplicação:

```bash
docker compose down
```

---

## Executando no GitHub Codespaces

Acesse o diretório do projeto:

```bash
cd /workspaces/BD_projeto_ProUni/app
```

Carregue as variáveis de ambiente:

```bash
set -a
source .env
set +a
```

Execute a aplicação:

```bash
python3 -m streamlit run dashboard/dashboard.py \
  --server.address 0.0.0.0 \
  --server.port 8501
```

---

## Tecnologias Utilizadas

* Python
* Streamlit
* MongoDB 
* Docker
* Docker Compose

## Fonte dos Dados

Os dados utilizados são provenientes do Programa Universidade para Todos (ProUni).

---

## Licença

Este projeto possui finalidade acadêmica e educacional.
