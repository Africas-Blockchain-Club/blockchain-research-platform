require("dotenv").config();
const { ethers } = require("ethers");
const fs = require("fs");

const RPC_URL = process.env.RPC_URL;
const PROVIDER = new ethers.JsonRpcProvider(RPC_URL);

const wallets = JSON.parse(fs.readFileSync("./wallets.json"));

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// -----------------------------
// METHOD 1: On-chain block scanning
// NOTE: ethers v6 removed provider.getHistory(). To scan raw blocks you need
// an archive node or a service like Alchemy's Asset Transfers API.
// This method is shown for educational purposes - use Method 2 in practice.
// -----------------------------
async function checkOnChainInteractions(startBlock = 0, endBlock = "latest") {
    console.log("\n🔍 METHOD 1: On-chain block scanning (requires archive node)");
    console.log("=============================================================");
    console.log("ℹ️  ethers v6 does not expose getHistory() - this method requires");
    console.log("   Alchemy's alchemy_getAssetTransfers API or a similar service.");
    console.log("   Skipping and recommending Method 2 (Etherscan) instead.\n");
    return [];
}

// -----------------------------
// METHOD 2: Blockscout API (primary for Scroll Sepolia)
// Fallback: Scrollscan if no Blockscout key
// -----------------------------
async function checkEtherscanInteractions(apiKey) {
    const blockscoutKey = process.env.BLOCKSCOUT_API_KEY;

    if (!blockscoutKey && !apiKey) {
        console.log("❌ No BLOCKSCOUT_API_KEY or ETHERSCAN_API_KEY in .env.");
        return [];
    }

    const usingBlockscout = !!blockscoutKey;
    const key = usingBlockscout ? blockscoutKey : apiKey;
    const baseUrl = usingBlockscout
        ? "https://scroll-sepolia.blockscout.com/api"
        : "https://api-sepolia.scrollscan.com/api";

    console.log(`\n🔍 METHOD 2: ${usingBlockscout ? "Blockscout" : "Scrollscan"} API`);
    console.log("=".repeat(usingBlockscout ? 28 : 26));

    const axios = require("axios");
    const walletAddresses = wallets.map(w => w.address.toLowerCase());
    const interactions = [];

    for (let i = 0; i < walletAddresses.length; i++) {
        const address = walletAddresses[i];
        console.log(`Checking wallet ${i + 1}/${walletAddresses.length}: ${address.substring(0, 10)}...`);

        try {
            // tokentx returns ERC20 transfers; txlist returns ETH-only transfers
            const url = `${baseUrl}?module=account&action=tokentx&address=${address}&startblock=0&endblock=99999999&sort=asc&apikey=${key}`;
            const response = await axios.get(url, { maxRedirects: 5 });

            const ok = response.data.status === "1" || response.data.message === "OK";
            if (ok && Array.isArray(response.data.result)) {
                for (const tx of response.data.result) {
                    const to = tx.to?.toLowerCase();
                    const from = tx.from?.toLowerCase();

                    for (const otherAddress of walletAddresses) {
                        const other = otherAddress.toLowerCase();

                        if (to === other && from === address && from !== to) {
                            interactions.push({
                                type: "TOKEN_SENT",
                                from: address,
                                to: otherAddress,
                                value: ethers.formatUnits(tx.value, parseInt(tx.tokenDecimal || "18")),
                                symbol: tx.tokenSymbol || "TOKEN",
                                hash: tx.hash,
                                blockNumber: parseInt(tx.blockNumber),
                                timestamp: new Date(parseInt(tx.timeStamp) * 1000),
                                gasUsed: tx.gasUsed,
                                gasPrice: tx.gasPrice
                            });
                        }
                    }
                }
            }

            await sleep(200);
        } catch (error) {
            console.log(`  Error: ${error.message}`);
        }
    }

    return interactions;
}

// -----------------------------
// METHOD 3: ERC20 Transfer event logs
// More targeted than full tx history - only shows token movements
// -----------------------------
async function checkTokenTransfers(tokenAddress, startBlock = 0, endBlock = "latest") {
    console.log("\n🔍 METHOD 3: ERC20 Transfer events");
    console.log("====================================");

    if (!tokenAddress || tokenAddress === "0x0000000000000000000000000000000000000000") {
        console.log("❌ No TOKEN address in .env. Skipping.");
        return [];
    }

    const tokenABI = [
        "event Transfer(address indexed from, address indexed to, uint256 value)",
        "function decimals() view returns (uint8)",
        "function symbol() view returns (string)"
    ];

    const token = new ethers.Contract(tokenAddress, tokenABI, PROVIDER);
    const walletAddresses = wallets.map(w => w.address.toLowerCase());
    const interactions = [];

    try {
        const symbol = await token.symbol();
        const decimals = await token.decimals();
        console.log(`Token: ${symbol} (${decimals} decimals)`);

        if (endBlock === "latest") {
            endBlock = await PROVIDER.getBlockNumber();
        }

        console.log(`Scanning blocks ${startBlock} → ${endBlock}\n`);

        for (const address of walletAddresses) {
            console.log(`Checking ${address.substring(0, 10)}...`);

            // Query logs where this address is the sender
            const sentFilter = token.filters.Transfer(address, null);
            const sentEvents = await token.queryFilter(sentFilter, startBlock, endBlock);

            // Query logs where this address is the receiver
            const receivedFilter = token.filters.Transfer(null, address);
            const receivedEvents = await token.queryFilter(receivedFilter, startBlock, endBlock);

            for (const event of sentEvents) {
                const to = event.args?.to?.toLowerCase();
                if (walletAddresses.includes(to) && to !== address) {
                    interactions.push({
                        type: "TOKEN_SENT",
                        from: address,
                        to,
                        amount: ethers.formatUnits(event.args?.value || 0, decimals),
                        symbol,
                        hash: event.transactionHash,
                        blockNumber: event.blockNumber
                    });
                }
            }

            for (const event of receivedEvents) {
                const from = event.args?.from?.toLowerCase();
                if (walletAddresses.includes(from) && from !== address) {
                    interactions.push({
                        type: "TOKEN_RECEIVED",
                        from,
                        to: address,
                        amount: ethers.formatUnits(event.args?.value || 0, decimals),
                        symbol,
                        hash: event.transactionHash,
                        blockNumber: event.blockNumber
                    });
                }
            }

            await sleep(100);
        }
    } catch (error) {
        console.log(`Error querying token transfers: ${error.message}`);
    }

    return interactions;
}

// -----------------------------
// Display results
// -----------------------------
function displayResults(interactions) {
    console.log("\n\n📊 INTERACTION RESULTS");
    console.log("======================");

    if (interactions.length === 0) {
        console.log("No interactions found between these wallets.");
        console.log("(Expected if wallets are freshly generated - they have no transaction history yet.)");
        return;
    }

    console.log(`Found ${interactions.length} interactions:\n`);

    const byType = {};
    interactions.forEach(i => {
        if (!byType[i.type]) byType[i.type] = [];
        byType[i.type].push(i);
    });

    for (const [type, txs] of Object.entries(byType)) {
        console.log(`\n${type} (${txs.length} transactions):`);
        console.log("-".repeat(50));

        txs.forEach((tx, idx) => {
            console.log(`${idx + 1}. ${tx.from.substring(0, 10)}... → ${tx.to.substring(0, 10)}...`);
            if (tx.value)  console.log(`   ETH:  ${tx.value}`);
            if (tx.amount) console.log(`   Token: ${tx.amount} ${tx.symbol || ""}`);
            console.log(`   Hash: ${tx.hash}`);
            if (tx.timestamp) console.log(`   Time: ${tx.timestamp}`);
        });
    }

    const walletSummary = {};
    interactions.forEach(tx => {
        if (!walletSummary[tx.from]) walletSummary[tx.from] = { sent: 0, received: 0 };
        if (!walletSummary[tx.to])   walletSummary[tx.to]   = { sent: 0, received: 0 };
        walletSummary[tx.from].sent++;
        walletSummary[tx.to].received++;
    });

    console.log("\n📈 SUMMARY");
    console.log("==========");
    for (const [address, stats] of Object.entries(walletSummary)) {
        console.log(`${address.substring(0, 15)}...: ${stats.sent} sent, ${stats.received} received`);
    }
}

// -----------------------------
// Main
// -----------------------------
async function main() {
    console.log("🚀 Wallet interaction analysis");
    console.log(`📊 Analysing ${wallets.length} wallets\n`);

    wallets.forEach((w, i) => console.log(`${i + 1}. ${w.address}`));

    const etherscanApiKey = process.env.ETHERSCAN_API_KEY || "";
    const tokenAddress = process.env.TOKEN;

    const currentBlock = await PROVIDER.getBlockNumber();
    const rangeBlocks = 10000;
    const startBlock = currentBlock - rangeBlocks;

    let allInteractions = [];

    await checkOnChainInteractions(startBlock, currentBlock);

    const etherscanInteractions = await checkEtherscanInteractions(etherscanApiKey);
    allInteractions = [...allInteractions, ...etherscanInteractions];

    if (tokenAddress && tokenAddress !== "0x0000000000000000000000000000000000000000") {
        const tokenInteractions = await checkTokenTransfers(tokenAddress, startBlock, currentBlock);
        allInteractions = [...allInteractions, ...tokenInteractions];
    }

    // Deduplicate by transaction hash
    const seen = new Set();
    const uniqueInteractions = allInteractions.filter(i => {
        if (seen.has(i.hash)) return false;
        seen.add(i.hash);
        return true;
    });

    displayResults(uniqueInteractions);

    if (uniqueInteractions.length > 0) {
        fs.writeFileSync("./interactions.json", JSON.stringify(uniqueInteractions, null, 2));
        console.log("\n💾 Saved to interactions.json");
    }

    console.log("\n✅ Analysis complete!");
}

main().catch(error => {
    console.error("❌ Error:", error.message);
    process.exit(1);
});
