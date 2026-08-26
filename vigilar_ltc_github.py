import requests
import os
import json

# ==== CONFIGURA SOLO ESTA LÍNEA (tu dirección no es secreta) ====
DIRECCION_LTC = "LKayyShop6r6Sfa7Fmwm6S8HgLZ5A1XRk5"
# ==================================================================

# Estos dos vienen de los "Secrets" de GitHub, no se escriben aquí
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["CHAT_ID"]

ARCHIVO_ESTADO = "ultimo_balance.json"

def obtener_balance(direccion):
    url = f"https://litecoinspace.org/api/address/{direccion}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    recibido = data["chain_stats"]["funded_txo_sum"] + data["mempool_stats"]["funded_txo_sum"]
    gastado = data["chain_stats"]["spent_txo_sum"] + data["mempool_stats"]["spent_txo_sum"]
    return recibido - gastado

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=15)

def leer_ultimo_balance():
    if os.path.exists(ARCHIVO_ESTADO):
        with open(ARCHIVO_ESTADO) as f:
            return json.load(f)["balance"]
    return None

def guardar_balance(balance):
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump({"balance": balance}, f)

def main():
    balance_actual = obtener_balance(DIRECCION_LTC)
    ultimo_balance = leer_ultimo_balance()

    if ultimo_balance is not None and balance_actual > ultimo_balance:
        diferencia = balance_actual - ultimo_balance
        mensaje = (
            f"💰 ¡Pago recibido!\n"
            f"Cantidad: {diferencia / 1e8:.8f} LTC\n"
            f"Nuevo balance: {balance_actual / 1e8:.8f} LTC"
        )
        enviar_telegram(mensaje)
        print(mensaje)
    else:
        print(f"Sin cambios. Balance actual: {balance_actual / 1e8:.8f} LTC")

    guardar_balance(balance_actual)

if __name__ == "__main__":
    main()
