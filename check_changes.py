import requests
import os

# --- CONFIGURACIÓN ---
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt"

# Esta línea lee la URL secreta que guardaste en Settings de GitHub
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

def enviar_slack(mensaje):
    if SLACK_URL:
        payload = {"text": mensaje}
        try:
            response = requests.post(SLACK_URL, json=payload)
            response.raise_for_status()
            print("Mensaje enviado a Slack correctamente.")
        except Exception as e:
            print(f"Error al enviar a Slack: {e}")
    else:
        print("Error: No se encontró la URL de Slack en los Secretos de GitHub.")

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    response = requests.get(url)
    return response.json()[0]['sha']

# --- LÓGICA PRINCIPAL ---
latest_sha = get_latest_commit_sha()

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last_sha = f.read().strip()
else:
    last_sha = ""

if latest_sha != last_sha:
    # Definimos el mensaje que verás en Slack
    texto_aviso = (
        f"🚀 *¡Cambio detectado en TDTChannels!*\n"
        f"Se han actualizado canales en el archivo `{FILE_PATH}`.\n"
        f"Ver detalles del cambio: https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/master/{FILE_PATH}"
    )
    
    print(f"Cambio detectado: {latest_sha}")
    enviar_slack(texto_aviso)
    
    # Guardamos el nuevo SHA para no repetir el aviso
    with open(STATE_FILE, "w") as f:
        f.write(latest_sha)
else:
    print("Sin cambios. Todo sigue igual.")
