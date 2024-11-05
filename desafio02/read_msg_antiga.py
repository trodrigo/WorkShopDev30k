import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from stellar_sdk import Keypair, Network, Server
from stellar_sdk.transaction_envelope import TransactionEnvelope
from stellar_sdk import Operation
from stellar_sdk.exceptions import NotFoundError
from stellar_sdk.exceptions import BadSignatureError

def read():
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)    
    # Quando o .env está na mesma pasta
    #load_dotenv() 
    #     
    # Configurações iniciais
    PRV_KEY = os.getenv('KEY_PRIVATE_ANT')
    sender_keypair = Keypair.from_secret(PRV_KEY)
    PUBLIC_KEY = sender_keypair.public_key
    # URL do Horizon na Standalone Network
    #SERVER_URL = "http://localhost:8000"
    #server = Server(horizon_url=SERVER_URL)
    #network_passphrase = Network.STANDALONE_NETWORK_PASSPHRASE
    # URL do Horizon na Main Net
    SERVER_URL = "https://horizon.stellar.org"
    server = Server(horizon_url=SERVER_URL)
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
    print(sender_keypair.public_key)

    # Ler o hash da transação do arquivo
    try:
        with open("tx_hash_ant.txt", "r") as f:
            tx_hash = f.read().strip()
    except FileNotFoundError:
        print("🚨 Arquivo 'tx_hash.txt' não encontrado. Execute o Script 1 primeiro.")
        return

    print(f"🔗 Hash da Transação: {tx_hash}")

    # Recuperar a transação pelo hash
    try:
        tx = server.transactions().transaction(tx_hash).call()
    except NotFoundError:
        print("🚫 Transação não encontrada na rede.")
        return
    except Exception as e:
        print("🚨 Erro ao recuperar a transação:")
        print(e)
        return

    # Recuperar o envelope XDR da transação
    try:
        envelope_xdr = tx["envelope_xdr"]
        te = TransactionEnvelope.from_xdr(envelope_xdr, network_passphrase)
    except Exception as e:
        print("🚨 Erro ao decodificar o envelope XDR:")
        print(e)
        return

    # Extrair a operação Manage Data com a chave "msg"
    manage_data_op = None
    for op in te.transaction.operations:
        x = isinstance(op, Operation)
        y = op.data_name == "desafio"
        if x and y:
            manage_data_op = op
            break

    if not manage_data_op:
        print(
            "🚫 Operação 'manage_data' com a chave 'msg' não encontrada na transação."
        )
        print(f"👀 {te.transaction.operations}")
        return

    # Extrair o valor da operação (assinatura em bytes)
    assinatura_bytes = manage_data_op.data_value

    # Codificar a assinatura em base64 para exibição
    assinatura_b64 = base64.b64encode(assinatura_bytes).decode()
    print(f"🗝️ Chave de Dados: {manage_data_op.data_name}")
    print(f"📝 Valor de Dados (base64): {assinatura_b64}")

    # Mensagem original
    mensagem = "DEV30K".encode()

    # Criar um objeto Keypair a partir da chave pública
    try:
        keypair = Keypair.from_public_key(PUBLIC_KEY)
    except Exception as e:
        print("🚨 Erro ao criar Keypair a partir da chave pública:")
        print(e)
        return

    # Verificar a assinatura
    try:
        keypair.verify(mensagem, assinatura_bytes)
        print(
            "✅ A assinatura é válida. A mensagem foi assinada pela chave pública fornecida."
        )
    except BadSignatureError:
        print(
            "❌ A assinatura é inválida. A mensagem não foi assinada pela chave pública fornecida."
        )
    except Exception as e:
        print("🚨 Erro ao verificar a assinatura:")
        print(e)

if __name__ == "__main__":
    read()        