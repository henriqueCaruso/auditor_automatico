# 🤖 Auditor Fiscal-Contábil Automático

Uma aplicação web construída com Streamlit para automatizar a conciliação entre relatórios fiscais e contábeis, identificando divergências e possíveis causas raiz a nível de nota fiscal.

![Screenshot do App](lofo_empresa.png) ---

## 🚀 Funcionalidades

* **Pré-Análise Rápida:** Validação instantânea da estrutura do arquivo Excel (`.xlsb`) antes do processamento.
* **Processamento Paralelo:** Utiliza múltiplos núcleos do processador para acelerar a análise das abas de Entradas e Saídas.
* **Conciliação por CFOP:** Relatório de alto nível com as divergências entre os valores totais do Razão Contábil e do Livro Fiscal.
* **Análise de Causa Raiz:** Realiza um "drill-down" para identificar as notas fiscais individuais que podem ter causado as divergências.
* **Interface Interativa:** Interface limpa e profissional com timer, barra de progresso e logs detalhados.

---

## 🛠️ Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar a aplicação na sua máquina.

**Pré-requisitos:**
* Python 3.8 ou superior
* Git

**Passos para Instalação (Windows):**

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
    cd NOME_DO_REPOSITORIO
    ```

2.  **Crie o Ambiente Virtual (venv):**
    ```powershell
    python -m venv venv
    ```

3.  **Ative o Ambiente Virtual:**
    ```powershell
    .\venv\Scripts\activate
    ```
    *(Você saberá que funcionou quando `(venv)` aparecer no seu terminal.)*

4.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute a Aplicação:**
    ```bash
    streamlit run app.py
    ```
    O aplicativo abrirá automaticamente no seu navegador.

---

## 📈 Como Contribuir e Atualizar no GitHub

Para adicionar novas funcionalidades ou corrigir bugs, siga este fluxo de trabalho básico do Git.

1.  **Sincronize com o Repositório Principal:** Antes de começar, sempre puxe as últimas alterações.
    ```bash
    git pull origin main
    ```

2.  **Crie uma Nova Branch:** Nunca trabalhe diretamente na branch `main`. Crie uma branch para sua nova funcionalidade.
    ```bash
    git checkout -b minha-nova-feature
    ```
    *(Substitua `minha-nova-feature` por um nome descritivo, como `melhorar-layout-tabelas`)*

3.  **Faça suas Alterações:** Modifique o código no `app.py`, adicione novas imagens, etc.

4.  **Adicione e Commite suas Mudanças:** Salve um "snapshot" do seu trabalho com uma mensagem clara.
    ```bash
    git add .
    git commit -m "Adiciona nova funcionalidade de exportar relatório"
    ```

5.  **Envie sua Branch para o GitHub:**
    ```bash
    git push origin minha-nova-feature
    ```

6.  **Crie um Pull Request (PR):** Vá até a página do seu repositório no GitHub. Você verá um aviso para criar um "Pull Request" da sua nova branch. Clique nele, descreva suas alterações e abra o PR para que as mudanças possam ser revisadas e integradas à branch `main`.