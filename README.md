# Pipeline de Dados com IoT e Docker

Projeto acadêmico da disciplina **Disruptive Architectures: IoT, Big Data e IA**.

## Objetivo

Construir um pipeline de dados que lê o conjunto **Temperature Readings: IoT Devices**, trata as colunas, grava as leituras em PostgreSQL executado em Docker e disponibiliza um dashboard interativo em Streamlit.

O dataset possui 5 colunas (`id`, `room_id/id`, `noted_date`, `temp`, `out/in`) e 97.606 registros. A fonte indicada no enunciado é o Kaggle.

## Estrutura

```text
pipeline_iot_docker/
├── data/
│   ├── README.md
│   └── sample_IOT-temp.csv
├── docs/
│   └── relatorio.md
├── sql/
│   ├── schema.sql
│   └── views.sql
├── src/
│   ├── pipeline.py
│   └── dashboard.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 1. Baixar o dataset

Baixe `IOT-temp.csv` no Kaggle e coloque-o em `data/IOT-temp.csv`.

Fonte:
https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

O arquivo de exemplo existente no projeto serve apenas para testar a estrutura; para a entrega acadêmica, use o CSV original do Kaggle.

## 2. Instalar dependências

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Subir PostgreSQL com Docker

```bash
docker compose up -d
```

Verifique:

```bash
docker ps
```

## 4. Processar os dados

```bash
python src/pipeline.py
```

O script:
- valida as colunas esperadas;
- converte `noted_date` para data/hora;
- converte `temp` para numérico;
- normaliza o indicador `out/in` para `location`;
- cria a tabela `temperature_readings`;
- grava os dados no PostgreSQL;
- cria as três views SQL.

## 5. Executar o dashboard

```bash
streamlit run src/dashboard.py
```

O dashboard apresenta:
1. média de temperatura por ambiente (`In`/`Out`);
2. quantidade de leituras por hora;
3. temperaturas máxima e mínima por dia.

## 6. Comandos Git

```bash
git init
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
git add .
git commit -m "Projeto inicial: Pipeline de Dados IoT"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

## Observação importante

O enunciado usa `device_id` apenas como exemplo de uma view. O dataset real disponibilizado possui `id`, `room_id/id`, `noted_date`, `temp` e `out/in`; por isso o projeto adapta a primeira view para comparar a média por local (`In`/`Out`) sem inventar uma coluna de dispositivo.
