import spotipy
import json
import re
import subprocess
import time
import os
import csv
import sys
from datetime import datetime
from datetime import date
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm
import random
import numpy as np
import shutil
import os

source_dir = '/content/drive/MyDrive/my_spc/'
target_dir = '/content/'

file_names = os.listdir(source_dir)

for file_name in file_names:
    shutil.copy(os.path.join(source_dir, file_name), target_dir)

json_files = [
    "/content/config.json",
    "/content/config1.json",
    "/content/config2.json",
]

# Escolha aleatória de um arquivo .json
chosen_json_file = random.choice(json_files)

# Carrega as credenciais do arquivo .json escolhido
with open(chosen_json_file, "r") as file:
    credentials = json.load(file)

client_id = credentials["client_id"]
client_secret = credentials["client_secret"]

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

try:
    os.remove("/content/.cache")
    # print("Arquivo .cache removido com sucesso!")
except FileNotFoundError:
    None

Path.cwd()
os.chdir("/content/temp")
Path.cwd()

# Lista com os caminhos dos scripts
def run_subprocess(script, *args):
    process = subprocess.run(["python", script] + list(args), capture_output=True)
    return process.returncode

A1 = "/content/my_spc/text1.py"
A2 = "/content/my_spc/text2.py"
A3 = "/content/my_spc/text3.py"


scripts = [A1,A2,A3]

def scale_to_log(val, min_val, max_val, scale_min, scale_max):
    log_min_val = np.log10(min_val)
    log_max_val = np.log10(max_val)

    log_val = np.log10(val)

    return ((log_val - log_min_val) / (log_max_val - log_min_val)) * (scale_max - scale_min) + scale_min


def get_track_info_from_playlist(url):
    # Extrair o ID da playlist da URL
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    if not match:
        print("URL da playlist inválida.")
        return

    playlist_id = match.group(1)

    # Fazer a requisição para a API do Spotify para obter informações da playlist
    playlist_info = sp.playlist(playlist_id)

    offset = 0
    limit = 100
    total_tracks = playlist_info["tracks"]["total"] 
    # Obtém o nome da playlist
    playlist_name = playlist_info["name"]

    # Trata o nome da playlist para que seja um nome de arquivo válido (remove caracteres especiais e espaços)
    valid_filename = "".join(c for c in playlist_name if c.isalnum() or c in (" ", ".")).rstrip()

    csv_file_path = (f"/content/drive/MyDrive/Meus Arquivos CSV/{valid_filename} - Playcounty.csv")

    print(f"Exportanto a playlist {valid_filename} - Playcounty")

    # Abre o arquivo de log para gravação
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Artista","Titulo","Views","Log/Views","Popularidade","Energia","Dancabilidade","BPM","Key","Ano","Lancamento","URL","ISRC","Explicit",])
        # Para cada música na playlist
        while True:
            # Recuperar as músicas da playlist com paginação
            results = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
            tracks = results["items"]

            if not tracks:
                break

            # Para cada música na playlist
            for i, item in enumerate(tqdm(tracks, total=total_tracks, initial=1, bar_format='{l_bar}{bar}{r_bar}')):

                total_tracks += 1
                indice1 = i+1

                # Extrair as informações da faixa
                track_info = item["track"]
                track_id = track_info["id"]  # Id da faixa

                # Obter as características de áudio para essa faixa
                audio_features = sp.audio_features([track_id])[
                    0
                ]  # Lembre-se de passar o ID da faixa como uma lista
                artist_id = track_info["artists"][0]["id"]
                artists = track_info["artists"]

                # Criar uma lista para armazenar os nomes dos artistas
                artist_names = []

                # Limitar o número de artistas a 3
                for artist in artists[:3]:
                    artist_names.append(artist["name"])

                # Juntar todos os nomes dos artistas em uma única string, separados por espaços
                artist_names_string = "; ".join(artist_names)

                track_name = track_info["name"]
                track_name = track_name.replace(" - ", " ")

                track_uri = track_info["uri"]
                track_id = track_info["id"]
                explicit = track_info["explicit"]
                resposta = ""

                if explicit:
                    resposta = "Com Palavrão"
                else:
                    resposta = "Sem Palavrão"
                album_name = track_info["album"]["name"]
                album_uri = track_info["album"]["uri"]
                album_id = track_info["album"]["id"]  # Aqui adicionamos a informação sobre o álbum
                popularity = track_info["popularity"]
                popularity = round(popularity / 10)
                popularity = 1 if popularity == 0 else popularity
                popularity = int(popularity)
                formatted_popularity = (f"{popularity:02d}" if popularity < 10 else f"{popularity}")
                track_url = track_info["external_urls"]["spotify"]
                isrc = track_info["external_ids"].get("isrc", "N/A")
                release_date_str = track_info["album"]["release_date"]
                danceability = audio_features["danceability"]
                danceability = round(audio_features["danceability"] * 10)
                formatted_danceability = (f"Dnc {danceability:02d}" if danceability < 10 else f"Dnc {danceability}")
                energy = audio_features["energy"]
                energy = round(audio_features["energy"] * 10)
                formatted_energy = (f"Nrg {energy:02d}" if energy < 10 else f"Nrg {energy}")
                tempo = audio_features["tempo"]
                key = audio_features["key"]
                camelot = [
                    "8B",
                    "3B",
                    "10B",
                    "5B",
                    "12B",
                    "7B",
                    "2B",
                    "9B",
                    "4B",
                    "11B",
                    "6B",
                    "1B",
                    "5A",
                    "10A",
                    "3A",
                    "8A",
                    "6A",
                    "11A",
                    "4A",
                    "9A",
                    "2A",
                    "7A",
                    "12A",
                    "1A",
                ]
                camelot_key = camelot[key if audio_features["mode"] == 1 else key + 12]
                bpm = round(tempo)
                bpm_string = str(bpm)
                release_date = track_info["album"]["release_date"]
                release_year = release_date.split("-")[0]

                if len(release_date) == 4:  # Apenas o ano está presente
                    release_date = f"{release_date}-03-05"

                release_date = datetime.strptime(release_date, "%Y-%m-%d").date()

                data_hoje = date.today()

                diferenca = (data_hoje - release_date).days
                semanas_age = (diferenca // 7) + 1
                semanas_age_string = str(semanas_age)

                release_date_string = release_date.strftime("%Y-%m-%d")

                try:
                    os.remove("/content/auth.json")
                    os.remove("/content/auth1.json")
                    os.remove("/content/auth2.json")
                except FileNotFoundError:
                    None

                # Selecionar o script baseado no índice atual
                index = total_tracks % len(scripts)

                # Obter o caminho do script a ser executado
                script = scripts[index]

                # print(f'{total_tracks}')  # Exibindo a contagem total de músicas

                # ...
                # Selecionar o script baseado no índice atual
                index = total_tracks % len(scripts)

                # Definir os argumentos para a chamada do subprocesso
                args = (
                    artist_id,
                    "-t",
                    track_id,
                    "-a",
                    album_uri,
                    "-an",
                    artist_names_string,
                    "-tn",
                    track_name,
                    "-rd",
                    release_date_string,
                    "-ma",
                    semanas_age_string,
                    "-u",
                    track_url,
                    "-p",
                    formatted_popularity,
                    "-e",
                    formatted_energy,
                    "-d",
                    formatted_danceability,
                    "-b",
                    bpm_string,
                    "-k",
                    camelot_key,
                    "-ex",
                    resposta,
                )

                # ...
                for i in range(index, len(scripts)):
                    returncode = run_subprocess(scripts[i], *args)
                    if returncode == 0:
                        with open(
                            "/content/fmt_playcount.txt", "r"
                        ) as file:
                            fmt_playcount = int(file.read())
                            formatted_fmt_playcount = f"{fmt_playcount:010d}"
                        os.remove("/content/fmt_playcount.txt")
                        break
                    elif i < len(scripts) - 1:  # Não é o último script na lista
                        print(
                            f"Subprocess failed with return code {returncode}, trying next script"
                        )
                    else:  # É o último script na lista
                        print(f"All subprocesses failed with return code {returncode}")
                # ...

                # Obtém os valores das variáveis
                formatted_fmt_playcount = formatted_fmt_playcount
                formatted_fmt_playcount1 = f"{fmt_playcount:010d}"
                artist_names = artist_names_string
                track_name = track_name
                release_date = release_date_string
                semanas_age = semanas_age_string
                track_url = track_url
                formatted_popularity = formatted_popularity
                formatted_energy = formatted_energy
                formatted_danceability = formatted_danceability
                bpm = bpm_string
                camelot_key = camelot_key
                resposta = resposta
                isrc = isrc
                release_year = release_year

                # Escreve uma linha no arquivo CSV com os valores das variáveis

                formatted_fmt_playcount = int(formatted_fmt_playcount)
                if formatted_fmt_playcount == 0:
                    scaled_value = 0
                else:
                    if formatted_fmt_playcount <= 1000000000:  # 1 bilhão
                        scaled_value = round(
                            scale_to_log(
                                formatted_fmt_playcount, 1000, 1000000000, 1, 79
                            )
                        )
                    else:
                        scaled_value = round(
                            scale_to_log(
                                formatted_fmt_playcount, 1000000001, 5000000000, 80, 100
                            )
                        )

                print(
                    indice1,
                    "-",
                    artist_names_string,
                    "-",
                    track_name,
                    "-",
                    formatted_fmt_playcount1,
                    "views",
                    "-",
                    "Popularidade",
                    scaled_value,
                    "-",
                    "Lançamento",
                    release_year,
                    script.split("/")[-1],
                )

                writer.writerow(
                    [   
                        indice1,
                        artist_names,
                        track_name,
                        formatted_fmt_playcount1,
                        scaled_value,
                        formatted_popularity,
                        formatted_energy,
                        formatted_danceability,
                        bpm,
                        camelot_key,
                        release_year,
                        release_date,
                        track_url,
                        isrc,
                        resposta,
                    ]
                )

                try:
                    os.remove("/content/auth.json")
                    os.remove("/content/auth1.json")
                    os.remove("/content/auth2.json")
                except FileNotFoundError:
                    None
            tqdm.write(f"Total Tracks: {total_tracks}")
            print(f"Arquivo {valid_filename}-spoty_conty.csv criado com sucesso")

            # incrementar o offset pela limitação para a próxima iteração
            offset += limit


# URL da playlist do Spotify
print("Programa para obter numero de visualizações de musicas do spotify")
print()
spotify_url = input("Digite a URL da playlist do Spotify: ")

# Chamar a função para obter as informações da playlist
get_track_info_from_playlist(spotify_url)
print()
