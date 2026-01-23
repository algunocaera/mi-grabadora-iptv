import requests
import os

# Configuración
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt" # Archivo para guardar el último cambio visto

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    response = requests.get(url)
    return response.json()[0]['sha']

def notify_and_update(sha):
    # 1. Aquí envías la notificación (ejemplo Telegram)
    print(f"¡Cambio detectado! Nuevo SHA: {sha}")
    # Puedes usar requests.post para enviar el aviso a tu móvil o app
    
    # 2. Aquí podrías descargar el contenido real del m3u8
    # raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/{FILE_PATH}"
    # content = requests.get(raw_url).text
    # enviar_a_mi_app(content)

# Lógica principal
latest_sha = get_latest_commit_sha()

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last_sha = f.read().strip()
else:
    last_sha = ""

if latest_sha != last_sha:
    notify_and_update(latest_sha)
    with open(STATE_FILE, "w") as f:
        f.write(latest_sha)
else:
    print("Sin cambios.")
