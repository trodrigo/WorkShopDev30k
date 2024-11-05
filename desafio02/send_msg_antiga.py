import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from stellar_sdk import Keypair, Network, Server, TransactionBuilder
from stellar_sdk.exceptions import NotFoundError
from requests import get, RequestException

def create_account(public_key, server):
    url = "http://localhost:8000/friendbot"
    params = {"addr": public_key}
    timeout = 30
    try:
        r = get(url, params=params, timeout=timeout)
        r.raise_for_status()
    except RequestException as e:
        raise ValueError(f"Erro ao obter fundos do Friendbot: {str(e)}") from e
    account = server.accounts().account_id(public_key).call()
    balances = account["balances"]
    print(f"✅ Conta criada com sucesso: {public_key}")
    print("🔄 Saldo da Conta:")
    for balance in balances:
        asset_type = balance["asset_type"]
        balance_amount = balance["balance"]
        print(f"   - Tipo de Ativo: {asset_type}, Saldo: {balance_amount}")
    return account

def write():
    dotenv_path = Path('../.env')
    load_dotenv(dotenv_path=dotenv_path)    
    # Quando o .env está na mesma pasta
    #load_dotenv() 

    # Configurações iniciais       
    PRV_KEY = os.getenv('KEY_PRIVATE_ANT')
    sender_keypair = Keypair.from_secret(PRV_KEY)
    # URL do Horizon na Standalone Network
    #server = Server(horizon_url="http://localhost:8000")
    #network_passphrase = Network.STANDALONE_NETWORK_PASSPHRASE
    
    server = Server(horizon_url="https://horizon.stellar.org")
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE

    print(sender_keypair.public_key)
    sender_account = validate_account(sender_keypair.public_key, server)

    # Mensagem a ser assinada
    mensagem = "DEV30K".encode()

    # Assinar a mensagem
    assinatura = sender_keypair.sign(mensagem)
    assinatura_b64 = base64.b64encode(assinatura).decode()
    print(f"Mensagem Assinada (base64): {assinatura_b64}")

    # Chave e valor para a operação manage_data
    data_key = "desafio"
    # Valor é a assinatura em bytes
    data_value = assinatura

    # Construir a transação
    transaction = (
        TransactionBuilder(
            source_account=sender_account,
            network_passphrase=network_passphrase,
            base_fee=100,
        )
        .set_timeout(30)
        .append_manage_data_op(data_key, data_value)
        .build()
    )

    # Assinar a transação
    transaction.sign(sender_keypair)

    # Enviar a transação
    try:
        response = server.submit_transaction(transaction)
        print("Transação enviada com sucesso!")
        print(f"Hash da Transação: {response['hash']}")

        # Salvar o hash da transação em um arquivo
        tx_hash = response["hash"]
        with open("tx_hash_ant.txt", "w", encoding="utf-8") as f:
            f.write(tx_hash)
        print("Hash da transação salvo em 'tx_hash_ant.txt'.")
    except Exception as e:
        print("Erro ao enviar a transação:")
        print(e)

def validate_account(public_key, server):
    try:
        return server.load_account(public_key)
    except NotFoundError:
        print("A conta de destino não existe!")
        print("Criando a conta...")
        return create_account(public_key, server)        

if __name__ == "__main__":
    write()