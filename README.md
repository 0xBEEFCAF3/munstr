<br/>

<div align="center" style="margin: 30px;">
  <img src="https://raw.githubusercontent.com/0xBEEFCAF3/munstr/assets/images/munstr-logo.png" style="width:250px;" align="center" /> 
<br />
<br />

</div>

<br />

<div align="center"><strong>Secure your Bitcoin with the Munstrous power of decentralized multi-signature technology</strong><br>🕸🕯 An open source Musig privacy based wallet 🕯🕸

<br />

</div>


<div align="center">

[![Bitcoin](https://img.shields.io/badge/Bitcoin-000?style=for-the-badge&logo=bitcoin&logoColor=white)](https://bitcoin.org) [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) 

[![GitHub tag](https://img.shields.io/github/tag/0xBEEFCAF3/munstr?include_prereleases=&sort=semver)](https://github.com/0xBEEFCAF3/munstr/releases/) [![License](https://img.shields.io/badge/License-MIT-blue)](#license)  [![issues - badge-generator](https://img.shields.io/github/issues/0xBEEFCAF3/munstr)](https://github.com/MichaelCurrin/badge-generator/issues)

</div>

<br/>
(TODO: Flow chart could go here)



## What is Munstr?
**Munstr** is a combination of Schnorr signature based **Musig** (multisignature) keys in a terminal based wallet using decentralized **Nostr** networks as a communication layer to facilitate a secure and encrypted method of transporting and digitally signing bitcoin transactions in a way that chain analysis cannot identify the nature and setup of the transaction data. To anyone observing the blockchain, Munstr transactions look like single key **Pay-to-Taproot** (P2TR) spends.

This is facilitated through an interactive, multi-signature (n-of-n) Bitcoin wallet that is designed to enable a group of signers to facilitate an interactive signing session for taproot based outputs that belong to an aggregated public key. 


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


## Getting started

1. Start virtualenv `python3 -m venv .venv`
2. `pip3 install -r requirements.txt`

### Running the coordinator

`python3 start_coordinator.py`

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

- Integrate MuSig 2


## TeamMunster

<a href="https://github.com/0xBEEFCAF3/munstr/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=0xBEEFCAF3/munstr" />
</a>


## License

Licensed under the MIT License, Copyright © 2023-present TeamMunstr