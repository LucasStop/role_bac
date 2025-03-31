# 🔐 Sistema de Controle de Acesso Discricionário

Este projeto é uma aplicação desktop com interface gráfica desenvolvida em **Python**, que simula um **sistema de controle de acesso discricionário**. Usuários têm permissões específicas (leitura, escrita e remoção) para manipular arquivos fictícios de diferentes tipos: **texto (.txt)**, **desenho (.draw)** e **planilha (.sheet)**.

---

## 👥 Equipe
- **Lucas Stopinski da Silva**

---

## 📂 Estrutura do Projeto

```
role_bac/
│
├── main.py                     # Arquivo principal para iniciar o app
├── constants.py                # Constantes do projeto (ex: caminhos, enums)
│
├── gui/
│   ├── auth_screen.py          # Telas de login e registro
│   ├── dashboard_screen.py     # Tela principal pós-login
│   ├── file_editor.py          # Editor de texto para .txt
│   ├── screens.py              # Ponto de entrada da GUI
│   ├── styles.py               # Tema visual da aplicação
│   ├── widgets.py              # Componentes reutilizáveis (labels, etc.)
│   └── editors/
│       ├── draw_editor.py      # Editor visual para arquivos .draw
│       └── sheet_editor.py     # Editor tipo planilha para arquivos .sheet
│
├── core/
│   ├── auth.py                 # Autenticação e registro
│   ├── user_data.py            # Dados dos usuários
│   ├── credentials.py          # Leitura/escrita de credenciais
│   ├── file_manager.py         # Gerencia arquivos locais
│   ├── security.py             # Controle de tentativas e bloqueios
│
├── utils/
│   └── crypto.py               # Hash, salt, verificação de senha
│
├── data/
│   ├── credentials.json        # Armazena usuários e senhas
│   ├── user_data.json          # Armazena dados como permissões, login, etc
│   └── arquivos/               # Arquivos criados pelos usuários (.txt, .draw, .sheet)

```

---

## ⚙️ Funcionalidades

### ✅ Autenticação
- Login com nome de usuário e senha (criptografada com `salt + SHA256`)
- Bloqueio temporário após 5 tentativas falhas

### ✅ Cadastro de Usuário
- No cadastro pode ser escolhido o nível de permissão (leitura, escrita, remoção)
- Senha é armazenada de forma segura (criptografada com `salt + SHA256`)
- Permissões são armazenadas individualmente por usuário

### ✅ Tipos de Arquivo Suportados

| Tipo     | Extensão  | Editor         |
|----------|-----------|----------------|
| Texto    | `.txt`    | Editor básico  |
| Desenho  | `.draw`   | Editor com canvas (pintura livre) |
| Planilha | `.sheet`  | Grade com células e valores |

---

## 🔐 Permissões

- Cada usuário possui 3 tipos de permissões:
  - `leitura` → Visualizar arquivos
  - `escrita` → Criar e editar arquivos
  - `remocao` → Excluir arquivos

---

## ▶️ Como executar o projeto

1. **Clone o repositório**
```bash
git clone https://github.com/LucasStop/role_bac.git
cd role_bac
```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado)**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute o projeto**
```bash
python main.py
```

---

## 📦 Dependências

O projeto utiliza apenas bibliotecas **padrão do Python**, como:

- `tkinter`
- `json`
- `hashlib`
- `datetime`
- `os`
- `secrets`

---

## 📁 Arquivos de Dados

- `data/credentials.json` → usuários e hashes de senha
- `data/user_data.json` → dados de login, permissões, etc.
- `data/arquivos/` → onde os arquivos criados são armazenados

---

## 📌 Observações

- O sistema é baseado em **recursos fictícios**: os arquivos não representam documentos reais do sistema operacional.
- O programa foi desenvolvido para fins educacionais e simula um modelo **discricionário** de controle de acesso.
- Todos os dados são armazenados localmente em arquivos `.json`.

---

## 💡 Exemplo de Execução

```
Usuário autenticado com sucesso!
Escolha a operação: (ler, escrever, apagar)
> escrever
Informe o nome do recurso:
> projeto_teste.draw
Acesso permitido.
```
