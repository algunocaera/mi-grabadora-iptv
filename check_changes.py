import requests
import os

# --- CONFIGURACIÓN ---
# Estos datos definen qué archivo estamos vigilando en el repo de LaQuay
REPO_OWNER = "LaQuay"
REPO_NAME = "TDTChannels"
FILE_PATH = "TELEVISION.md"
STATE_FILE = "last_sha.txt"  # Archivo que sirve de "memoria" para el script

# URL segura que GitHub le pasa al script desde los "Secrets"
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")

def enviar_slack(mensaje):
    """Envía la notificación al canal de Slack configurado."""
    if SLACK_URL:
        payload = {"text": mensaje}
        try:
            response = requests.post(SLACK_URL, json=payload)
            if response.status_code == 200:
                print("✅ Mensaje enviado a Slack con éxito.")
            else:
                print(f"❌ Error en Slack: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión al intentar enviar a Slack: {e}")
    else:
        print("⚠️ Error: No se ha encontrado la variable SLACK_WEBHOOK_URL.")

def get_latest_commit_sha():
    """Consulta la API de GitHub para obtener el SHA del último cambio del archivo."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?path={FILE_PATH}&per_page=1"
    try:
        response = requests.get(url)
        
        # Manejo de errores de la API (ej: límite de peticiones o caída del servicio)
        if response.status_code != 200:
            print(f"❌ Error de GitHub API: {response.status_code}")
            return None
            
        data = response.json()
        if not data:
            print("❓ No se encontraron commits para este archivo.")
            return None
            
        # Retornamos el código único (SHA) del commit
        return data[0]['sha']
    except Exception as e:
        print(f"❌ Error al consultar la API de GitHub: {e}")
        return None

# --- LÓGICA PRINCIPAL ---
def main():
    latest_sha = get_latest_commit_sha()

    if latest_sha:
        # 1. Leer el último SHA que guardamos en la ejecución anterior
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                last_sha = f.read().strip()
        else:
            last_sha = ""

        # 2. Comparar: si el SHA de GitHub es distinto al guardado, hay novedad
        if True:
            print(f"🔔 ¡Cambio detectado! SHA nuevo: {latest_sha}")
            
            # Formateamos el mensaje para Slack con negritas y enlace
            texto_aviso = (
                f"🚀 *¡Nueva actualización en TDTChannels!*\n"
                f"Se han detectado cambios en la lista de canales.\n"
                f"🔗 *Ver cambios:* https://github.com/{REPO_OWNER}/{REPO_NAME}/commits/master/{FILE_PATH}"
            )
            
            enviar_slack(texto_aviso)
            
            # 3. Guardar el nuevo SHA para que no nos vuelva a avisar de lo mismo
            with open(STATE_FILE, "w") as f:
                f.write(latest_sha)
        else:
            print("😴 Sin cambios. Todo sigue igual.")
    else:
        print("🚫 No se pudo realizar la comprobación en esta vuelta.")

if __name__ == "__main__":
    main()
