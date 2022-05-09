# potoforio
Potoforio is free, open source, extreme privacy crypto portfolio manager. We DO NOT collect ANY data. Never.

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/misaka-eth/potoforio.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/misaka-eth/potoforio/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/misaka-eth/potoforio.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/misaka-eth/potoforio/alerts/)

---
Potoforio use third part provider for data like price wallet balances and asset price.

- Providers
  - BalanceProviders
    - [Beaconchain.com](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/beaconchain/beaconchain.py)
    - [Blockchain.com](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/blockchain/blockchain.py)
    - [Crypto.org](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/cryptocom/cryptocom.py)
    - [Etherscan.io](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/etherscan/etherscan.py)
    - [Ethplorer.io](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/ethplorer/ethplorer.py)
    - [Litecoinblockexplorer.net](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/litecoinblockexplorer/litecoinblockexplorer.py)
    - [Polygonscan.com](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/polygonscan/polygonscan.py)
    - [Xrpscan.com](https://github.com/misaka-eth/potoforio/tree/main/potoforio/providers/xrpscan)
  - PriceProviders
    - [Coingecko.com](https://github.com/misaka-eth/potoforio/tree/main/potoforio/providers/coingecko)
  - NFTProviders
    - [Crypto.org](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/cryptocom/cryptocom.py)
    - [Alchemy (Ethereum and Polygon)](https://github.com/misaka-eth/potoforio/blob/main/potoforio/providers/alchemy/alchemy.py)