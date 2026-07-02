require("dotenv").config();
const { ethers } = require("ethers");
const fs = require("fs");

const RPC_URL = process.env.RPC_URL;
const TOKEN = process.env.TOKEN;
const CONTRACT = process.env.CONTRACT;

// The minimum ABI needed to read ERC20 token data
// An ABI tells ethers.js how to communicate with the smart contract
const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function symbol() view returns (string)",
    "function decimals() view returns (uint8)"
];

const provider = new ethers.JsonRpcProvider(RPC_URL);
const token = new ethers.Contract(TOKEN, ERC20_ABI, provider);

const wallets = JSON.parse(fs.readFileSync("./wallets.json"));

async function main() {
    const symbol = await token.symbol();
    const decimals = await token.decimals();

    console.log("Token:", symbol);
    console.log("Decimals:", decimals);
    console.log("(Token amounts are stored as integers on-chain. decimals tells us where the decimal point goes.)\n");

    let total = 0n; // BigInt - required because blockchain values can exceed JS number precision

    console.log("========================");
    console.log("CONTRACT BALANCE");
    console.log("========================");

    const contractBal = await token.balanceOf(CONTRACT);
    console.log(`${CONTRACT}: ${ethers.formatUnits(contractBal, decimals)} ${symbol}`);
    total += contractBal;

    console.log("\n========================");
    console.log("WALLET BALANCES");
    console.log("========================");

    for (const w of wallets) {
        if (!w.address) continue;

        const bal = await token.balanceOf(w.address);
        console.log(`${w.address} → ${ethers.formatUnits(bal, decimals)} ${symbol}`);
        total += bal;
    }

    console.log("\n========================");
    console.log("TOTAL ACROSS ALL TRACKED ADDRESSES");
    console.log("========================");
    console.log(`TOTAL: ${ethers.formatUnits(total, decimals)} ${symbol}`);

    console.log("\nDone.");
}

main().catch(console.error);
