<br/>

<div align="center" style="margin: 30px;">
  <img src="https://github.com/0xBEEFCAF3/munstr/blob/main/assets/images/munstr-logo.png?raw=true" align="center" /> 
<br />
<br />
</div>


<div align="center"><strong>Secure your Bitcoin with the Munstrous power of decentralized multi-signature technology</strong><br>🕸🕯 An open source Musig privacy based wallet 🕯🕸
<br />
<br />
</div>


<div align="center">

[![Bitcoin](https://img.shields.io/badge/Bitcoin-000?style=for-the-badge&logo=bitcoin&logoColor=white)](https://bitcoin.org) [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) 

[![GitHub tag](https://img.shields.io/github/tag/0xBEEFCAF3/munstr?include_prereleases=&sort=semver)](https://github.com/0xBEEFCAF3/munstr/releases/) [![License](https://img.shields.io/badge/License-MIT-blue)](#license)  [![issues - badge-generator](https://img.shields.io/github/issues/0xBEEFCAF3/munstr)](https://github.com/MichaelCurrin/badge-generator/issues)

</div>

<br/>

## What is Munstr?
**Munstr** is a combination of Schnorr signature based **Musig** (multisignature) keys in a terminal based wallet using decentralized **Nostr** networks as a communication layer to facilitate a secure and encrypted method of transporting and digitally signing bitcoin transactions in a way that chain analysis cannot identify the nature and setup of the transaction data. To anyone observing the blockchain, Munstr transactions look like single key **Pay-to-Taproot** (P2TR) spends.

This is facilitated through an interactive, multi-signature (n-of-n) Bitcoin wallet that is designed to enable a group of signers to coordinate an interactive signing session for taproot based outputs that belong to an aggregated public key. 

<div align="center" style="margin: 30px;">
  <img src="https://github.com/0xBEEFCAF3/munstr/blob/main/assets/images/on_chain_tx.png?raw=true" align="center" /> 
<br />
<br />
</div>


## Disclaimer
This software is beta and should not be used for any real funds. Code and authors are subject to change. The maintainers take no responsiblity for any lost funds or damages incurred.


## Key Features

🌐 **Open source** for anyone to use or to contribute to

🔐 **Multisignature** keysets to reduce single key risk

🔀 **Encrypted Communications** with Nostr decentralized events

💪 **Taproot** supported outputs 


## Architecture
There are three major components to Munstr.

### Signer
The signer is responsible for using private keys in a multisignature keyset to digitally sign a **partially signed bitcoin transaction** (PSBT).

### Nostr
The Nostr decentralized network acts as a transport and communications layer for PSBT data. 

### Coordinator 
Coordinators act as a mediator between digital signers and wallets.  The coordinator facilitates digital signatures from each required (n-of-n) key signers and assists in broadcasting the fully signed transaction. 

### Flow
<div align="center" style="margin: 30px;">
  <img src="https://github.com/0xBEEFCAF3/munstr/blob/main/assets/images/flow.png?raw=true" align="center" /> 
<br />
<br />
</div>

## Getting started

1. Start virtualenv `python3 -m venv .venv`
2. `pip3 install -r requirements.txt`

### Running the coordinator

1. Initialize the persistent storage: Create a `src/coordinator/db.json` file from the provided `db.template.json`.
    ```
    cp src/coordinator/db.template.json src/coordinator/db.json
    ```
2. Start the coordinator
    ```
    python3 start_coordinator.py
    ```

### Running a signer

`python3 start_signer.py`


## Standing on the shoulders of giants

In addition to the libraries listed in `requirements.txt`, this project also uses:

- Code from the Bitcoin Optech Taproot & Schnorr workshop, specifically the Python test framework. The `test_framework` folder has been brought into our project and renamed to `src/bitcoin`.
- [1313 Mockingbird Lane](https://www.dafont.com/1313-mockingbird-lane.font) font by Jeff Bensch
- [Frankenstein Emoji](https://www.pngwing.com/en/free-png-yziyw)
- [Markdown Badges](https://github.com/Ileriayo/markdown-badges
) by Ileriayo


## Future goals

- MuSig 2 enhancements
- More accurate transaction fee estimation
- Better nostr encrypted DM support
- Custom nostr relay servers
- Custom nostr PSBT event types 
- Node connectivity
  - Sovereign TX lookup & broadcast
- Seed Phrases & xpubs
- Hardware Wallet support
  - SeedSigner (Taproot incoming)
  - Blockstream Jade


## TeamMunstr

<a href="https://github.com/0xBEEFCAF3">
  <img src="https://avatars.githubusercontent.com/u/24356537?s=120&v=4" />
</a>
<a href="https://github.com/satsie">
  <img src="https://avatars.githubusercontent.com/u/1823216?s=120&v=4" />
</a>
<a href="https://github.com/ronaldstoner">
  <img src="https://avatars.githubusercontent.com/u/6909088?s=120&v=4" />
</a>


## License

Licensed under the MIT License, Copyright © 2023-present TeamMunstr
