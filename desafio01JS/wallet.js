var StellarSdk = require('@stellar/stellar-sdk');

const pair = StellarSdk.Keypair.random();
console.log("Public Key: ", pair.publicKey());
console.log("Secret Key: ", pair.secret());