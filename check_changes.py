import requests
import os

# --- CONFIGURACIÓN ---
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt"
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

def enviar_slack(mensaje):
    if SLACK_URL:
        payload = {"text": mensaje}
        requests.post(SLACK_URL, json=payload)

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    response = requests.get(url)
    
    # Si GitHub nos da error (por ejemplo, por límite de velocidad)
    if response.status_code != 200:
        print(f"Error de GitHub API: {response.status_code}")
        return None
        
    data = response.json()
    if not data:
        print("No se encontraron commits para este archivo.")
        return None
        
    return data[0]['sha']

# --- LÓGICA PRINCIPAL ---
latest_sha = get_latest_commit_sha()

if latest_sha:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_sha = f.read().strip()
    else:
        last_sha = ""

    if latest_sha != last_sha:
        texto = f"🚀 *¡Actualización en IPTVChannels!* \nSe han detectado cambios. \nVer aquí: https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/master/{FILE_PATH}"
        enviar_slack(texto)
        with open(STATE_FILE, "w") as f:
            f.write(latest_sha)
        print(f"Cambio detectado y avisado: {latest_sha}")
    else:
        print("Sin cambios.")
else:
    print("No se pudo obtener el SHA. Reintentando en la próxima hora.")
