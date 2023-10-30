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

[![GitHub tag](https://img.shields.io/github/tag/0xBEEFCAF3/munstr?include_prereleases=&sort=semver)](https://github.com/0xBEEFCAF3/munstr/releases/) [![License](https://img.shields.io/badge/License-MIT-blue)](#license)  [![issues - badge-generator](https://img.shields.io/github/issues/0xBEEFCAF3/munstr)](https://github.com/0xBEEFCAF3/munstr)

</div>

<br/>

## What is Munstr?
**Munstr** (MuSig + Nostr) is a combination of Schnorr signature based **MuSig** (multisignature) keys in a terminal based wallet using decentralized **Nostr** networks as a communication layer to facilitate a secure and encrypted method of transporting and digitally signing bitcoin transactions in a way that chain analysis cannot identify the nature and setup of the transaction data. To anyone observing the blockchain, Munstr transactions look like single key **Pay-to-Taproot** (P2TR) spends.

This is facilitated through an interactive, multi-signature (n-of-n) Bitcoin wallet that is designed to enable a group of signers to coordinate an interactive signing session for taproot based outputs that belong to an aggregated public key. 

<br />

<div align="center" style="margin: 30px;">
  <img src="https://github.com/0xBEEFCAF3/munstr/blob/main/assets/images/on_chain_tx.png?raw=true" align="center" /> 
<br />
<br />
</div>


## Disclaimer
This software is beta and should not be used for any real funds. Code and authors are subject to change. The maintainers take no responsibility for any lost funds or damages incurred.


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
    ./start_coordinator.py
    ```
Possible arguments:

- `--show`: Show active relays via [nostr watch](https://nostr.watch/relays/find)
- `--add`: Add new relays ex: ``` ./start_coordinator --add [relay1] [relay2] ...```

### Running a signer

``` 
./start_signer.py
```


Possible arguments:

- `--wallet_id`: The coordinator persists wallets by ID with some associated information. Default is none.
- `--key_seed`: An optional seed to use when initializing the signer's keys. Not recommended for anything other than testing.
- `--nonce_seed`: An optional seed to use when creating nonces. Not recommended for anything other than testing.
- `--show`: Show active relays via [nostr watch](https://nostr.watch/relays/find)
- `--add`: Add new relays ex: ``` ./start_signer -add [relay1] [relay2] ...```

### Completing an end-to-end test

1. Start the coordinator
2. In a separate terminal window, start a signer (Signer1) and use the `--key_seed` option to set a seed for the key, and the `--nonce_seed` option to set the nonce seed (must be an integer). Example: `./start_signer.py --key_seed=key0 --nonce_seed=256`
3. Signer1: Execute the "new wallet" command. When prompted to specify a quorum, enter "2". Take note of the wallet ID that is returned.
4. In a separate terminal window, start a second signer (Signer2) with the `--wallet_id` flag set to the wallet ID that was returned in the previous step. Example: `./start_signer.py --key_seed=key1 --nonce_seed=256 --wallet_id=527f0dee-8b2a-45a1-87c6-98e9b6f642f7`
5. Have each signer send keys to the coordinator (`send pk` command)
6. Have each signer get an address from the coordinator (`address`). Confirm that the addresses are the same. This address corresponds to an aggregate pubkey that combines the keys of each signer.
7. Outside of Munstr, fund the address.
8. Have one signer initiate a spend by using the `spend` command.
9. Execute the `sign` command from each of the signers. After all signers have provided nonces, the coordinator will return the aggregate nonce, and the signers will be prompted to provide a partial signature. The coordinator will then aggregate the signatures and provide a raw hex transaction that is ready for broadcast!

## Demo 
[![Munstr Demo](https://img.youtube.com/vi/9AhzEatrZbg/0.jpg)](https://www.youtube.com/watch?v=9AhzEatrZbg)

## Presentation 
[Presentation Deck](https://docs.google.com/presentation/d/1UlT6VwL7sNL3wtElnNe2ITDrrGDHLcnl6U_Gsl02dtY/edit?usp=sharing)

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


## Standing on the shoulders of giants

In addition to the libraries listed in `requirements.txt`, this project also uses:

- Code from the Bitcoin Optech Taproot & Schnorr workshop, specifically the Python test framework. The `test_framework` folder has been brought into our project and renamed to `src/bitcoin`.
- [Nostr](https://github.com/nostr-protocol/nostr) by fiatjaf
- [1313 Mockingbird Lane](https://www.dafont.com/1313-mockingbird-lane.font) font by Jeff Bensch
- [Frankenstein Emoji](https://www.pngwing.com/en/free-png-yziyw)
- [Markdown Badges](https://github.com/Ileriayo/markdown-badges) by Ileriayo
- [ANSI FIGlet font: Bloody](https://patorjk.com/software/taag/#p=display&f=Bloody&t=munstr)



## Resources

**MuSig**

- \[blog\] [Taproot and MuSig2 Recap by Elle Mouton](https://ellemouton.com/posts/taproot-prelims/)
- [video] [Tim Ruffing | MuSig 2: Simple Two-Round Schnorr Multi-Signatures](https://youtu.be/DRzDDFetS3E)

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
