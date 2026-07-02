require("dotenv").config();
const { ethers } = require("ethers");
const fs = require("fs");

const NUM_WALLETS = 5;

// METHOD 1: Random wallets - each has its own independent mnemonic
async function createWallets() {
    console.log("Creating random wallets...\n");

    const wallets = [];

    for (let i = 1; i <= NUM_WALLETS; i++) {
        const wallet = ethers.Wallet.createRandom();

        wallets.push({
            id: i,
            address: wallet.address,
            privateKey: wallet.privateKey,
            mnemonic: wallet.mnemonic?.phrase || "N/A"
        });

        console.log(`Wallet ${i}:`);
        console.log(`  Address:     ${wallet.address}`);
        console.log(`  Private Key: ${wallet.privateKey}`);
        console.log(`  Mnemonic:    ${wallet.mnemonic?.phrase || "N/A"}`);
        console.log("---");
    }

    fs.writeFileSync("./wallets.json", JSON.stringify(wallets, null, 2));
    console.log(`\n✅ Created ${NUM_WALLETS} wallets and saved to wallets.json`);
}

// METHOD 2: Deterministic (HD) wallets - all derived from one master mnemonic
// This is how Metamask and hardware wallets work internally
async function createDeterministicWallets() {
    console.log("Creating deterministic HD wallets from a single mnemonic...\n");

    const mnemonic = ethers.Mnemonic.fromEntropy(ethers.randomBytes(32));
    console.log(`Master Mnemonic: ${mnemonic.phrase}\n`);
    console.log("⚠️  Save this mnemonic - it can regenerate all wallets below.\n");

    const wallets = [];

    for (let i = 0; i < NUM_WALLETS; i++) {
        // BIP-44 derivation path: m / purpose' / coin_type' / account' / change / index
        // 60 = Ethereum coin type
        const derivationPath = `m/44'/60'/0'/0/${i}`;
        const hdNode = ethers.HDNodeWallet.fromMnemonic(mnemonic, derivationPath);

        wallets.push({
            id: i + 1,
            address: hdNode.address,
            privateKey: hdNode.privateKey,
            derivationPath,
            mnemonic: i === 0 ? mnemonic.phrase : "(same master mnemonic as wallet 1)"
        });

        console.log(`Wallet ${i + 1}:`);
        console.log(`  Address:         ${hdNode.address}`);
        console.log(`  Private Key:     ${hdNode.privateKey}`);
        console.log(`  Derivation Path: ${derivationPath}`);
        console.log("---");
    }

    fs.writeFileSync("./wallets.json", JSON.stringify(wallets, null, 2));
    console.log(`\n✅ Created ${NUM_WALLETS} deterministic wallets saved to wallets.json`);
}

// Switch between methods by commenting/uncommenting below
createWallets();
// createDeterministicWallets();
