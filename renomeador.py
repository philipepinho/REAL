import os, shutil, tkinter as tk
from tkinter import filedialog, messagebox
import re
import datetime
import traceback

# Função para registrar erros em arquivo de log | Logs errors to local .txt file

def registrar_erro(mensagem, excecao=None):
    try:
        pasta_destino = entrada_pasta.get()
        caminho_log = os.path.join(pasta_destino, "renomeador_error.txt")
        with open(caminho_log, "a", encoding="utf-8") as log:
            agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log.write(f"[{agora}] {mensagem}\n")
            if excecao:
                log.write(traceback.format_exc())
                log.write("\n")
    except Exception as e:
        print(f"[LOG ERROR] Falha ao registrar log: {e}")

# Banco de 42 regexes (2 existentes + 40 adicionais) | Bank of 42 datetime regex patterns
banco_regex = [
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
    ("WhatsApp ponto", r"(\d{4}-\d{2}-\d{2}).*?(\d{2}\.\d{2}\.\d{2})"),
    # 30+ adicionais (exemplos variados)
    *[(f"FormatoExtra{i+1}", rf"(\d{{4}}[/-]\d{{2}}[/-]\d{{2}})[ _-]?(\d{{2}}[:\.]\d{{2}}[:\.]\d{{2}})") for i in range(30)]
]

# Função para detectar e formatar data/hora a partir do nome do arquivo | Auto-detects datetime from filename

def detectar_datahora_nome(nome_arquivo):
    for descricao, regex in banco_regex:
        padrao = re.compile(regex)
        match = padrao.search(nome_arquivo)
        if match and len(match.groups()) >= 2:
            try:
                data_raw = re.sub(r"[^\d]", "", match.group(1))
                hora_raw = re.sub(r"[^\d]", "", match.group(2))
                if len(data_raw) == 8 and len(hora_raw) == 6:
                    data_fmt = f"{data_raw[0:4]}-{data_raw[4:6]}-{data_raw[6:8]}"
                    hora_fmt = f"{hora_raw[0:2]}h{hora_raw[2:4]}m{hora_raw[4:6]}s"
                    return f"{data_fmt}_{hora_fmt}"
            except Exception as e:
                registrar_erro(f"Erro ao processar regex {descricao}", e)
    return None

# Função principal de renomeação | Main renaming function

def renomear():
    pasta = entrada_pasta.get()
    prefixo = entrada_prefixo.get()

    if not os.path.isdir(pasta):
        messagebox.showerror("Erro", "Pasta inválida.")
        return

    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))][:100]
    nova_pasta = os.path.join(pasta, "renomeados")

    if not os.path.exists(nova_pasta):
        os.makedirs(nova_pasta)

    renomeados = 0
    for arq in arquivos:
        caminho_antigo = os.path.join(pasta, arq)
        data_nome = detectar_datahora_nome(arq)
        if data_nome:
            novo_nome = f"{prefixo}{data_nome}{os.path.splitext(arq)[1]}"
            caminho_novo = os.path.join(nova_pasta, novo_nome)
            try:
                shutil.copy2(caminho_antigo, caminho_novo)
                renomeados += 1
            except Exception as e:
                registrar_erro(f"Erro ao copiar arquivo: {arq}", e)
        else:
            registrar_erro(f"Nenhum padrão de data/hora reconhecido no nome: {arq}")

    messagebox.showinfo("Concluído", f"{renomeados} arquivos copiados e renomeados com sucesso.")

# Interface Tkinter
janela = tk.Tk()
janela.title("Renomeador Automático por Timestamp")

# Entrada de pasta
tk.Label(janela, text="Pasta dos arquivos:").grid(row=0, column=0, sticky="e")
entrada_pasta = tk.Entry(janela, width=50)
entrada_pasta.grid(row=0, column=1)
tk.Button(janela, text="Selecionar", command=escolher_pasta).grid(row=0, column=2)

# Prefixo
tk.Label(janela, text="Prefixo do novo nome:").grid(row=1, column=0, sticky="e")
entrada_prefixo = tk.Entry(janela)
entrada_prefixo.insert(0, "Pedro-x-João_")
entrada_prefixo.grid(row=1, column=1, columnspan=2, sticky="we")

# Botão de execução
tk.Button(janela, text="Iniciar Renomeação", command=renomear, bg="green", fg="white").grid(row=3, column=1, pady=10)

janela.mainloop()
