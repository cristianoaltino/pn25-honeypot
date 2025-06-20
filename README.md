# 🐍 Desenvolvendo Honeypots com Python

> **Evento:** Python Nordeste 2025  
> **Palestrante:** Cristiano Altino  
> **Tema:** Criação de honeypots educativos em Python para detecção, monitoramento e análise de ataques em tempo real.


## 📌 Sobre o projeto

Este repositório contém o código-fonte, exemplos de honeypots e materiais práticos utilizados na palestra **Desenvolvendo Honeypots com Python**, apresentada no Python Nordeste 2025.

O objetivo é demonstrar, de forma didática e controlada, como criar honeypots customizados com Python para simular serviços vulneráveis, registrar tentativas de ataque e analisar o comportamento de agentes maliciosos em tempo real.



## 📁 Estrutura do repositório

```plaintext
.
├── honeypots/
│   ├── ssh_honeypot.py
│   ├── http_honeypot.py
│   ├── ftp_honeypot.py
│   └── mysql_honeypot.py
├── logs
├── requirements.txt
├── .env.example
└── README.md
```


## ⚙️ Pré-requisitos

- Python 3.8+
- Git
- Docker (opcional, para executar laboratórios em containers)


## 🚀 Como executar

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/cristianoaltino/pn25-honeypot.git
   cd pn25-honeypot
   python -m venv venv
