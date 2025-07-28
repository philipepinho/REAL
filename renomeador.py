import os, shutil, tkinter as tk  # bibliotecas padrão para arquivos, cópias e interface gráfica | std libraries for file ops and GUI
from tkinter import filedialog, messagebox, ttk  # módulos específicos do Tkinter | specific Tkinter modules
import re  # biblioteca para expressões regulares | regex library
import datetime  # para registrar data e hora | for timestamps
import traceback  # para capturar rastros completos de erro | full error trace

def registrar_erro(mensagem, excecao=None):
    """Grava erros em um arquivo de log local | Logs errors to local file"""
    try:
        nome_arquivo = "renomeador_error.log"
        caminho_log = os.path.join(os.getcwd(), nome_arquivo)  # mesmo diretório do .py/.exe | same folder
        with open(caminho_log, "a", encoding="utf-8") as log:
            agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{agora}] {mensagem}\n")
            if excecao:
                log.write(traceback.format_exc())
                log.write("\n")
    except Exception as e:
        # Evita travar mesmo se o log falhar | fail-safe log fallback
        print(f"[LOG ERROR] Falha ao registrar log: {e}")

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
    ("WhatsApp - Data e Hora (2025-07-27 15.06.02)", r"(\d{4}-\d{2}-\d{2}).*?(\d{2}\.\d{2}\.\d{2})"),
    ("WhatsApp - Nome do Arquivo (2023-07-19 à(s) 09.58.02)", r"(\d{4}-\d{2}-\d{2}).*?(\d{2}\.\d{2}\.\d{2})")
]

def escolher_pasta():
    caminho = filedialog.askdirectory()  # abre janela para selecionar pasta | open folder dialog
    entrada_pasta.delete(0, tk.END)  # limpa o campo atual | clear field
    entrada_pasta.insert(0, caminho)  # insere novo caminho | insert new path

def normalizar_datahora(data, hora):
    data = re.sub(r"[^\d]", "-", data)[:10]  # Normaliza a data
    hora = re.sub(r"[^\d]", "", hora)  # remove tudo que não for número
    if len(hora) == 6:
        return f"{data}_{hora[:2]}h{hora[2:4]}m{hora[4:6]}s"
    else:
        return f"{data}_00h00m00s"

def extrair_data_arquivo(caminho_arquivo, regex):
    nome_arquivo = os.path.basename(caminho_arquivo)  # obtém apenas o nome do arquivo | get filename only
    try:
        padrao = re.compile(regex)
        match = padrao.search(nome_arquivo)
        if match:
            if len(match.groups()) >= 2:
                # Elimina caracteres não numéricos | Remove non-numeric characters
                data_raw = re.sub(r"[^\d]", "", match.group(1))  # exemplo: 2023-07-19 → 20230719
                hora_raw = re.sub(r"[^\d]", "", match.group(2))  # exemplo: 09.58.02 → 095802

                # Formata data como AAAA-MM-DD | Format date
                if len(data_raw) == 8:
                    data_fmt = f"{data_raw[0:4]}-{data_raw[4:6]}-{data_raw[6:8]}"
                else:
                    data_fmt = "0000-00-00"

                # Formata hora como HHhMMmSSs | Format hour
                if len(hora_raw) == 6:
                    hora_fmt = f"{hora_raw[0:2]}h{hora_raw[2:4]}m{hora_raw[4:6]}s"
                else:
                    hora_fmt = "00h00m00s"

                return f"{data_fmt}_{hora_fmt}"
            else:
                return match.group(0)
    except Exception as e:
        print(f"[ERRO] {nome_arquivo}: {e}")
    return None

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
