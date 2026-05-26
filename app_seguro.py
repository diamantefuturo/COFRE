# =========================================================
# COFRE DE DADOS - SISTEMA DE AUDITORIA E CRIPTOGRAFIA
# =========================================================

# =========================================================
# IMPORTAÇÕES
# =========================================================

import os
import csv
import json
import shutil
import hashlib

from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from cryptography.fernet import Fernet

# =========================================================
# CONFIGURAÇÕES INICIAIS
# =========================================================

ARQUIVO_LOG = "auditoria.txt"

arquivo_selecionado = None

# =========================================================
# FUNÇÃO DE LOG
# =========================================================

def registrar_log(mensagem):
    """
    Registra eventos no arquivo de auditoria.
    """

    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
        log.write(f"[{data_hora}] {mensagem}\n")


# =========================================================
# FUNÇÃO PARA LIMPAR TABELA
# =========================================================

def limpar_tabela():
    """
    Remove dados antigos da tabela.
    """

    for item in tabela.get_children():
        tabela.delete(item)


# =========================================================
# FUNÇÃO PARA SELECIONAR ARQUIVO
# =========================================================

def selecionar_arquivo():
    """
    Abre a janela de seleção de arquivos.
    """

    global arquivo_selecionado

    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[
            ("Arquivos Permitidos", "*.txt *.csv *.json *.xml"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if caminho:
        arquivo_selecionado = caminho

        label_arquivo.config(
            text=f"Arquivo Selecionado:\n{arquivo_selecionado}"
        )

        registrar_log(
            f"Arquivo selecionado: {Path(caminho).name}"
        )


# =========================================================
# FUNÇÃO PARA VISUALIZAR ARQUIVO
# =========================================================

def visualizar_conteudo():
    """
    Lê o arquivo e exibe o conteúdo.
    """

    if not arquivo_selecionado:
        messagebox.showwarning(
            "Aviso",
            "Selecione um arquivo primeiro."
        )
        return

    limpar_tabela()

    extensao = Path(arquivo_selecionado).suffix.lower()

    try:

        # =================================================
        # CSV
        # =================================================
        if extensao == ".csv":

            with open(
                arquivo_selecionado,
                "r",
                encoding="utf-8"
            ) as arquivo:

                leitor = csv.reader(arquivo)

                dados = list(leitor)

                if not dados:
                    messagebox.showinfo(
                        "Informação",
                        "CSV vazio."
                    )
                    return

                colunas = dados[0]

                tabela["columns"] = colunas
                tabela["show"] = "headings"

                for coluna in colunas:
                    tabela.heading(coluna, text=coluna)
                    tabela.column(coluna, width=150)

                for linha in dados[1:]:
                    tabela.insert("", tk.END, values=linha)

        # =================================================
        # JSON
        # =================================================
        elif extensao == ".json":

            with open(
                arquivo_selecionado,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados_json = json.load(arquivo)

            tabela["columns"] = ("Conteúdo JSON",)
            tabela["show"] = "headings"

            tabela.heading(
                "Conteúdo JSON",
                text="Conteúdo JSON"
            )

            tabela.column(
                "Conteúdo JSON",
                width=900
            )

            texto_json = json.dumps(
                dados_json,
                indent=4,
                ensure_ascii=False
            )

            for linha in texto_json.splitlines():
                tabela.insert("", tk.END, values=(linha,))

        # =================================================
        # TXT
        # =================================================
        elif extensao == ".txt":

            with open(
                arquivo_selecionado,
                "r",
                encoding="utf-8"
            ) as arquivo:

                linhas = arquivo.readlines()

            tabela["columns"] = ("Conteúdo TXT",)
            tabela["show"] = "headings"

            tabela.heading(
                "Conteúdo TXT",
                text="Conteúdo TXT"
            )

            tabela.column(
                "Conteúdo TXT",
                width=900
            )

            for linha in linhas:
                tabela.insert(
                    "",
                    tk.END,
                    values=(linha.strip(),)
                )

        # =================================================
        # XML
        # =================================================
        elif extensao == ".xml":

            import xml.etree.ElementTree as ET

            arvore = ET.parse(arquivo_selecionado)

            raiz = arvore.getroot()

            tabela["columns"] = ("Tag", "Texto")
            tabela["show"] = "headings"

            tabela.heading("Tag", text="Tag")
            tabela.heading("Texto", text="Texto")

            tabela.column("Tag", width=250)
            tabela.column("Texto", width=650)

            for elemento in raiz.iter():

                tabela.insert(
                    "",
                    tk.END,
                    values=(
                        elemento.tag,
                        str(elemento.text).strip()
                        if elemento.text
                        else ""
                    )
                )

        else:
            messagebox.showerror(
                "Erro",
                "Formato não suportado."
            )
            return

        registrar_log(
            f"O arquivo {Path(arquivo_selecionado).name} foi visualizado."
        )

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            f"Falha ao visualizar arquivo:\n{erro}"
        )


# =========================================================
# FUNÇÃO DE CRIPTOGRAFIA
# =========================================================

def copiar_criptografar():
    """
    Criptografa e salva uma cópia segura.
    """

    if not arquivo_selecionado:
        messagebox.showwarning(
            "Aviso",
            "Selecione um arquivo primeiro."
        )
        return

    try:

        pasta_destino = filedialog.askdirectory(
            title="Escolha a pasta de destino"
        )

        if not pasta_destino:
            return

        # =============================================
        # LEITURA DO ARQUIVO ORIGINAL
        # =============================================

        with open(
            arquivo_selecionado,
            "rb"
        ) as arquivo:

            conteudo_original = arquivo.read()

        # =============================================
        # GERAÇÃO DA CHAVE
        # =============================================

        chave = Fernet.generate_key()

        fernet = Fernet(chave)

        # =============================================
        # CRIPTOGRAFIA
        # =============================================

        conteudo_criptografado = fernet.encrypt(
            conteudo_original
        )

        nome_original = Path(arquivo_selecionado).stem

        arquivo_criptografado = os.path.join(
            pasta_destino,
            f"{nome_original}_criptografado.enc"
        )

        with open(
            arquivo_criptografado,
            "wb"
        ) as arquivo:

            arquivo.write(conteudo_criptografado)

        # =============================================
        # SALVANDO CHAVE
        # =============================================

        arquivo_chave = os.path.join(
            pasta_destino,
            f"{nome_original}_chave.key"
        )

        with open(
            arquivo_chave,
            "wb"
        ) as chave_file:

            chave_file.write(chave)

        # =============================================
        # GERAÇÃO HASH SHA256
        # =============================================

        hash_sha256 = hashlib.sha256(
            conteudo_original
        ).hexdigest()

        arquivo_hash = os.path.join(
            pasta_destino,
            f"{nome_original}_hash.txt"
        )

        with open(
            arquivo_hash,
            "w",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(
                f"HASH SHA256:\n{hash_sha256}"
            )

        # =============================================
        # LOG
        # =============================================

        registrar_log(
            f"Arquivo copiado de "
            f"{arquivo_selecionado} "
            f"para {pasta_destino} "
            f"com criptografia. "
            f"Hash gerado: {hash_sha256}"
        )

        messagebox.showinfo(
            "Sucesso",
            "Arquivo criptografado com sucesso."
        )

    except Exception as erro:

        messagebox.showerror(
            "Erro",
            f"Falha na criptografia:\n{erro}"
        )


# =========================================================
# CRIAÇÃO DA JANELA
# =========================================================

janela = tk.Tk()

janela.title("Cofre de Dados")
janela.geometry("1100x650")
janela.configure(bg="#F0F0F0")

# =========================================================
# LOG DE INICIALIZAÇÃO
# =========================================================

registrar_log("Sistema Iniciado")

# =========================================================
# TÍTULO
# =========================================================

titulo = tk.Label(
    janela,
    text="COFRE DE DADOS",
    font=("Arial", 20, "bold"),
    bg="#F0F0F0",
    fg="#222222"
)

titulo.pack(pady=10)

# =========================================================
# LABEL DO ARQUIVO
# =========================================================

label_arquivo = tk.Label(
    janela,
    text="Nenhum arquivo selecionado",
    font=("Arial", 10),
    bg="#F0F0F0",
    fg="blue"
)

label_arquivo.pack(pady=5)

# =========================================================
# FRAME DOS BOTÕES
# =========================================================

frame_botoes = tk.Frame(
    janela,
    bg="#F0F0F0"
)

frame_botoes.pack(pady=10)

# =========================================================
# BOTÃO SELECIONAR
# =========================================================

botao_selecionar = tk.Button(
    frame_botoes,
    text="Selecionar Arquivo",
    width=25,
    height=2,
    command=selecionar_arquivo
)

botao_selecionar.grid(row=0, column=0, padx=10)

# =========================================================
# BOTÃO VISUALIZAR
# =========================================================

botao_visualizar = tk.Button(
    frame_botoes,
    text="Visualizar Conteúdo",
    width=25,
    height=2,
    command=visualizar_conteudo
)

botao_visualizar.grid(row=0, column=1, padx=10)

# =========================================================
# BOTÃO CRIPTOGRAFAR
# =========================================================

botao_criptografar = tk.Button(
    frame_botoes,
    text="Copiar e Criptografar",
    width=25,
    height=2,
    command=copiar_criptografar
)

botao_criptografar.grid(row=0, column=2, padx=10)

# =========================================================
# TABELA
# =========================================================

frame_tabela = tk.Frame(janela)

frame_tabela.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

scroll_y = tk.Scrollbar(frame_tabela)

scroll_y.pack(
    side="right",
    fill="y"
)

tabela = ttk.Treeview(
    frame_tabela,
    yscrollcommand=scroll_y.set
)

tabela.pack(
    fill="both",
    expand=True
)

scroll_y.config(
    command=tabela.yview
)

# =========================================================
# EXECUÇÃO DA JANELA
# =========================================================

janela.mainloop()