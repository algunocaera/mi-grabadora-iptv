import requests
import os

# --- CONFIGURACIÓN ---
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt"
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Lista de canales de tu interés extraída de la imagen
CANALES_A_VIGILAR = [
    "Onda Cádiz", "101TV Axarquía", "101TV Ronda", "Estepona TV",
    "Canal Coín", "Sal TV", "Torremolinos TV", "Diez TV Las Villas",
    "Cancionero TV", "Tuya La Janda TV"
]

def enviar_slack(mensaje):
    """Envía la notificación a Slack."""
    if SLACK_URL:
        payload = {"text": mensaje}
        try:
            response = requests.post(SLACK_URL, json=payload)
            if response.status_code == 200:
                print("✅ Alerta de canal enviada a Slack.")
            else:
                print(f"❌ Error en Slack: {response.status_code}")
        except Exception as e:
            print(f"❌ Fallo de conexión: {e}")

def get_file_content():
    """Descarga el contenido de TELEVISION.md para buscar los canales."""
    url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/master/{FILE_PATH}"
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else None
    except:
        return None

def get_latest_commit_sha():
    """Obtiene el SHA del último cambio."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    try:
        response = requests.get(url)
        return response.json()[0]['sha'] if response.status_code == 200 else None
    except:
        return None

def main():
    latest_sha = get_latest_commit_sha()
    if not latest_sha:
        print("🚫 No se pudo conectar con la API de GitHub.")
        return

    # Leer memoria del último cambio avisado
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_sha = f.read().strip()
    else:
        last_sha = ""

    # 1. ¿Hay un cambio nuevo en el repositorio?
    if latest_sha != last_sha:
        print(f"🔎 Cambio detectado. Analizando contenido para canales específicos...")
        contenido = get_file_content()
        
        if contenido:
            # 2. Filtrar: Buscar cuáles de tus canales están en el texto
            encontrados = [c for c in CANALES_A_VIGILAR if c in contenido]
            
            if encontrados:
                # Si encuentra canales de tu lista, envía la alerta personalizada
                lista_canales = "\n• " + "\n• ".join(encontrados)
                texto = (
                    f"📺 *¡Novedades en tus canales favoritos!*\n"
                    f"Se ha detectado una actualización que afecta a:\n{lista_canales}\n\n"
                    f"🔗 *Revisar cambios:* https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/master/{FILE_PATH}"
                )
                enviar_slack(texto)
                print(f"🎯 Canales detectados y avisados: {encontrados}")
            else:
                print("😴 El cambio no afecta a tus canales de interés. No se envía alerta.")

            # 3. Guardar el SHA para estar al día, aunque no hayamos avisado por falta de coincidencia
            with open(STATE_FILE, "w") as f:
                f.write(latest_sha)
    else:
        print("😴 Sin cambios nuevos desde la última revisión.")

if __name__ == "__main__":
    main()
