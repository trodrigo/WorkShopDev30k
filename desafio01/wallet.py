from stellar_sdk import Keypair

keypair = Keypair.random()
print("Public Key: " + keypair.public_key)
print("Secret Seed: " + keypair.secret)