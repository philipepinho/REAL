import os, shutil, tkinter as tk  # bibliotecas padrão para arquivos, cópias e interface gráfica | std libraries for file ops and GUI
from tkinter import filedialog, messagebox, ttk  # módulos específicos do Tkinter | specific Tkinter modules
import re  # biblioteca para expressões regulares | regex library

# Lista com as 10 opções de regex e sua descrição legível | List of 10 regex patterns and user-friendly labels
opcoes_regex = [
    ("YYYYMMDD-HHMMSS", r"(\d{8})-(\d{6})"),
    ("YYYY-MM-DD_HHMMSS", r"(\d{4}-\d{2}-\d{2})_(\d{6})"),
    ("DD/MM/YYYY HH:MM:SS", r"(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}:\d{2})"),
    ("YYYY/MM/DD HHMMSS", r"(\d{4}/\d{2}/\d{2}) (\d{6})"),
    ("YYYY.MM.DD HH:MM:SS", r"(\d{4}\.\d{2}\.\d{2}) (\d{2}:\d{2}:\d{2})"),
    ("DD-MM-YYYY_HHMMSS", r"(\d{2}-\d{2}-\d{4})_(\d{6})"),
    ("DDMMYYYYHHMMSS", r"(\d{2}\d{2}\d{4})(\d{6})"),
    ("YYYY/MM/DD_HH:MM:SS", r"(\d{4}/\d{2}/\d{2})_(\d{2}:\d{2}:\d{2})"),
    ("YYYY-MM-DDTHH:MM:SS", r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})"),
    ("YYYYMMDDHHMMSS", r"(\d{8})(\d{6})"),
    ("WhatsApp - Data e Hora (2025-07-27 15.06.02)", r"(\d{4}-\d{2}-\d{2}).*?(\d{2}\.\d{2}\.\d{2})")
]

def escolher_pasta():
    caminho = filedialog.askdirectory()  # abre janela para selecionar pasta | open folder dialog
    entrada_pasta.delete(0, tk.END)  # limpa o campo atual | clear field
    entrada_pasta.insert(0, caminho)  # insere novo caminho | insert new path

def normalizar_datahora(data, hora):
    data = re.sub(r"[^\d]", "-", data)[:10]  # substitui separadores por hífens | replace date separators
    hora = hora.replace(":", "h").replace("m", "").replace("s", "")[:6]  # formata hora | format hour
    return f"{data}_{hora[:2]}h{hora[2:4]}m{hora[4:6]}s"  # retorna formato final | return final format

def extrair_data_arquivo(caminho_arquivo, regex):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:  # abre o arquivo como texto | open file as text
            conteudo = f.read()  # lê conteúdo inteiro | read content
            padrao = re.compile(regex)  # compila a regex fornecida | compile given regex
            match = padrao.search(conteudo)  # procura o padrão no conteúdo | search pattern in content
            if match:
                if len(match.groups()) >= 2:  # se houver pelo menos 2 grupos (data + hora) | if there are at least 2 groups
                    return normalizar_datahora(match.group(1), match.group(2))  # normaliza e retorna | normalize and return
                else:
                    return match.group(0)  # retorna grupo único, sem normalização | return single group
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")  # loga erro | log error
    return None  # retorno padrão | default return

def renomear():
    pasta = entrada_pasta.get()  # obtém caminho da pasta | get folder path
    prefixo = entrada_prefixo.get()  # obtém prefixo inserido pelo usuário | get user prefix
    idx_regex = combobox_regex.current()  # obtém índice da regex escolhida | get regex index

    if not os.path.isdir(pasta):  # verifica se a pasta existe | check if folder exists
        messagebox.showerror("Erro", "Pasta inválida.")  # alerta de erro | error alert
        return

    regex = opcoes_regex[idx_regex][1]  # obtém a regex correspondente ao índice | get regex by index
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))][:100]  # lista até 100 arquivos | list up to 100 files
    nova_pasta = os.path.join(pasta, "renomeados")  # define pasta de destino | target folder

    if not os.path.exists(nova_pasta):
        os.makedirs(nova_pasta)  # cria pasta se não existir | create folder if missing

    renomeados = 0  # contador de arquivos | file counter
    for arq in arquivos:
        caminho_antigo = os.path.join(pasta, arq)  # caminho completo original | full old path
        data_nome = extrair_data_arquivo(caminho_antigo, regex)  # extrai timestamp do conteúdo | extract timestamp
        if data_nome:
            novo_nome = f"{prefixo}{data_nome}{os.path.splitext(arq)[1]}"  # constrói novo nome com extensão | build new filename
            caminho_novo = os.path.join(nova_pasta, novo_nome)  # novo caminho completo | new full path
            shutil.copy2(caminho_antigo, caminho_novo)  # copia arquivo com metadados | copy file
            renomeados += 1  # incrementa contador | increment counter
        else:
            print(f"Regex não encontrou padrão em: {arq}")  # log se regex falha | log if regex fails

    messagebox.showinfo("Concluído", f"{renomeados} arquivos renomeados e copiados com sucesso.")  # alerta final | success message

# Início da GUI | GUI start
janela = tk.Tk()
janela.title("Renomeador por Timestamp")  # título da janela | window title

# Linha 1: Campo de pasta | Folder input field
tk.Label(janela, text="Pasta dos arquivos:").grid(row=0, column=0, sticky="e")
entrada_pasta = tk.Entry(janela, width=50)
entrada_pasta.grid(row=0, column=1)
tk.Button(janela, text="Selecionar", command=escolher_pasta).grid(row=0, column=2)

# Linha 2: Campo de prefixo | Prefix input field
tk.Label(janela, text="Prefixo do novo nome:").grid(row=1, column=0, sticky="e")
entrada_prefixo = tk.Entry(janela)
entrada_prefixo.insert(0, "Pedro-x-João_")  # valor inicial padrão | default value
entrada_prefixo.grid(row=1, column=1, columnspan=2, sticky="we")

# Linha 3: Combobox de regex | Regex pattern selector
tk.Label(janela, text="Formato de data/hora no conteúdo:").grid(row=2, column=0, sticky="e")
combobox_regex = ttk.Combobox(janela, width=47, values=[op[0] for op in opcoes_regex], state="readonly")
combobox_regex.current(0)  # seleciona primeira opção por padrão | default select first
combobox_regex.grid(row=2, column=1, columnspan=2)

# Botão final | Start button
tk.Button(janela, text="Iniciar Renomeação", command=renomear, bg="green", fg="white").grid(row=3, column=1, pady=10)

janela.mainloop()  # mantém janela aberta | keeps window open
