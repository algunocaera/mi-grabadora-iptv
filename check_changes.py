import requests
import os

# --- CONFIGURACIÓN ---
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt"
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Tu lista de interés
CANALES_A_VIGILAR = [
    "Onda Cádiz", "101TV Axarquía", "101TV Ronda", "Estepona TV",
    "Canal Coín", "Sal TV", "Torremolinos TV", "Diez TV Las Villas",
    "Cancionero TV", "Tuya La Janda TV"
]

def enviar_slack(mensaje):
    if SLACK_URL:
        payload = {"text": mensaje}
        requests.post(SLACK_URL, json=payload)

def get_latest_commit_details():
    """Obtiene el SHA y los cambios específicos (patch) del último commit."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        sha = response.json()[0]['sha']
        # Segunda petición para ver qué líneas exactas cambiaron
        detail_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{sha}"
        detail_response = requests.get(detail_url)
        if detail_response.status_code == 200:
            commit_data = detail_response.json()
            for file in commit_data['files']:
                if file['filename'] == FILE_PATH:
                    return sha, file.get('patch', '')
    return None, None

def main():
    latest_sha, patch = get_latest_commit_details()
    if not latest_sha: return

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_sha = f.read().strip()
    else:
        last_sha = ""

    if latest_sha != last_sha:
        # ANALIZAMOS EL PARCHE: Solo buscamos en líneas que empiezan con '+' (añadidas/modificadas)
        lineas_cambiadas = [line for line in patch.split('\n') if line.startswith('+')]
        cambios_detectados = []

        for canal in CANALES_A_VIGILAR:
            for linea in lineas_cambiadas:
                if canal in linea:
                    cambios_detectados.append(canal)
                    break # No repetir el mismo canal si sale en varias líneas

        if cambios_detectados:
            lista_nombres = "\n• " + "\n• ".join(cambios_detectados)
            texto = (
                f"✅ *Actualización detectada en:* {lista_nombres}\n"
                f"🔗 *Ver detalle:* https://github.com/{REPO_OWNER}/{REPO_NAME}/commit/{latest_sha}"
            )
            enviar_slack(texto)
        
        # Guardamos el SHA para no repetir aviso
        with open(STATE_FILE, "w") as f:
            f.write(latest_sha)

if __name__ == "__main__":
    main()
