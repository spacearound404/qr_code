# SMART-CONTRACT-TEST
## Start up
1. add ether to address throw https://www.rinkebyfaucet.com/
2. add data to `secret.json`
```
{
	"mnemonic": "menmonic from acc",
	"accountPrivateKey": "",
	"alchemyApiKey": ""
}
```
3. `npx ipfs-car --pack images --output images.car`
4. upload file to https://nft.storage/files/
5. copy `img id folder` and past in `metadata/1`
6. `npx ipfs-car --pack metadata --output metadata.car`
7. upload file to https://nft.storage/files/
8. copy `metadata id folder`
9. `npx hardhat run --network rinkeby scripts/deploy.js`
10. change contract address in `hardhat.config.js `
11. `npx hardhat set-base-token-uri --base-url "https://ipfs.io/ipfs/metadata id folder/metadata/"`
12. `npx hardhat mint --address 0x...`


## Usefull links
- https://rinkeby.etherscan.io
- https://docs.openzeppelin.com/contracts/4.x/erc721
- https://docs.openzeppelin.com/learn/developing-smart-contracts
- https://github.com/neha01/nft-demo/blob/master/contracts/ArtCollectible.sol
- https://solidity-by-example.org/app/erc721/
- https://docs.opensea.io/docs/minting-from-your-new-contract-and-improvements
- https://ipld.io/specs/transport/car/carv1/
- https://github.com/ipfs-shipyard/py-ipfs-http-client
- https://hardhat.org/guides/create-task.html
- https://hardhat.org/tutorial/testing-contracts.html
- https://testnets.opensea.io/
