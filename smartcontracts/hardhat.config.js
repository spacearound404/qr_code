/**
 * @type import('hardhat/config').HardhatUserConfig
 */
const { alchemyApiKey, accountPrivateKey } = require('./secrets.json');
const fetch = require("node-fetch");
const { getContractAt } = require("@nomiclabs/hardhat-ethers/internal/helpers");

require('@nomiclabs/hardhat-ethers');
require("@nomiclabs/hardhat-web3");

function getProvider() {
  return ethers.getDefaultProvider("rinkeby", {
      alchemy: accountPrivateKey,
  });
}

function getAccount() {
  return new ethers.Wallet(accountPrivateKey, getProvider());
}

function getContract(contractName, hre) {
  const account = getAccount();
  return getContractAt(hre, contractName, "0x98Ba15e2378Bf9927d0ed58bB86442a3b0f3481E", account);
}

task("mint", "Mints from the TESTQC9 contract")
.addParam("address", "The address to receive a token")
.setAction(async function (taskArguments, hre) {
    const contract = await getContract("TESTQC9", hre);
    const transactionResponse = await contract.mintTo(taskArguments.address, {
        gasLimit: 500_000,
    });
    console.log(`Transaction Hash: ${transactionResponse.hash}`);
});

task("set-base-token-uri", "Sets the base token URI for the deployed smart contract")
.addParam("baseUrl", "The base of the tokenURI endpoint to set")
.setAction(async function (taskArguments, hre) {
    const contract = await getContract("TESTQC9", hre);
    const transactionResponse = await contract.setBaseTokenURI(taskArguments.baseUrl, {
        gasLimit: 500_000,
    });
    console.log(`Transaction Hash: ${transactionResponse.hash}`);
});


task("token-uri", "Fetches the token metadata for the given token ID")
.addParam("tokenId", "The tokenID to fetch metadata for")
.setAction(async function (taskArguments, hre) {
    const contract = await getContract("TESTQC9", hre);
    const response = await contract.tokenURI(taskArguments.tokenId, {
        gasLimit: 500_000,
    });
    
    const metadata_url = response;
    console.log(`Metadata URL: ${metadata_url}`);

    const metadata = await fetch(metadata_url).then(res => res.json());
    console.log(`Metadata fetch response: ${JSON.stringify(metadata, null, 2)}`);
    // console.log(metadata)
});

module.exports = {
  networks: {
    rinkeby: {
      url: `https://eth-rinkeby.alchemyapi.io/v2/${alchemyApiKey}`,
      accounts: [`0x${accountPrivateKey}`],
    },
  },
  solidity: "0.8.4",
};