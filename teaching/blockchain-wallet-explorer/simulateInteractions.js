require("dotenv").config();
const { ethers } = require("ethers");
const fs = require("fs");
const axios = require("axios");

const RPC_URL    = process.env.RPC_URL;
const TOKEN      = (process.env.TOKEN || "").toLowerCase();
const provider   = new ethers.JsonRpcProvider(RPC_URL);
const wallets    = JSON.parse(fs.readFileSync("./wallets.json"));

if (wallets.length < 5) {
    console.error("❌ Need at least 5 wallets. Run: node createWallets.js");
    process.exit(1);
}

// -----------------------------
// API helpers
// -----------------------------
function getApiConfig() {
    const blockscoutKey = process.env.BLOCKSCOUT_API_KEY;
    const scrollscanKey = process.env.ETHERSCAN_API_KEY;
    return {
        key:     blockscoutKey || scrollscanKey,
        baseUrl: blockscoutKey
            ? "https://scroll-sepolia.blockscout.com/api"
            : "https://api-sepolia.scrollscan.com/api",
        name: blockscoutKey ? "Blockscout" : "Scrollscan"
    };
}

async function fetchTokenTx(address, api) {
    const url = `${api.baseUrl}?module=account&action=tokentx&address=${address}&sort=asc&apikey=${api.key}`;
    const res = await axios.get(url, { maxRedirects: 5 });
    const ok  = res.data.status === "1" || res.data.message === "OK";
    if (!ok || !Array.isArray(res.data.result)) return [];
    // filter to the token we care about (if TOKEN is set in .env)
    return TOKEN
        ? res.data.result.filter(t => t.contractAddress.toLowerCase() === TOKEN)
        : res.data.result;
}

function formatTx(tx) {
    return {
        from:        tx.from.toLowerCase(),
        to:          tx.to?.toLowerCase(),
        value:       ethers.formatUnits(tx.value, parseInt(tx.tokenDecimal || "18")),
        symbol:      tx.tokenSymbol || "TOKEN",
        hash:        tx.hash,
        blockNumber: parseInt(tx.blockNumber),
        timestamp:   new Date(parseInt(tx.timeStamp) * 1000)
    };
}

function dedupe(arr) {
    const seen = new Set();
    return arr.filter(i => {
        if (seen.has(i.hash)) return false;
        seen.add(i.hash);
        return true;
    });
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// -----------------------------
// Step 1: interactions between wallets we already know about
// -----------------------------
async function fetchKnownInteractions(api) {
    const knownAddresses = wallets.map(w => w.address.toLowerCase());
    const interactions   = [];

    console.log(`\n🔍 Step 1 - Interactions between your wallets (via ${api.name})...`);

    for (const address of knownAddresses) {
        try {
            const txs = await fetchTokenTx(address, api);
            for (const tx of txs) {
                const from = tx.from.toLowerCase();
                const to   = tx.to?.toLowerCase();
                if (knownAddresses.includes(from) && knownAddresses.includes(to) && from !== to) {
                    interactions.push(formatTx(tx));
                }
            }
            await sleep(200);
        } catch (e) {
            console.log(`  Error for ${address}: ${e.message}`);
        }
    }

    return dedupe(interactions);
}

// -----------------------------
// Step 2: trace who sent tokens INTO our wallets from outside
//         then fetch everything that origin wallet sent
// -----------------------------
async function traceOrigins(api) {
    const knownAddresses = wallets.map(w => w.address.toLowerCase());
    const ZERO_ADDRESS   = "0x0000000000000000000000000000000000000000";

    console.log("\n🔍 Step 2 - Tracing token origins...");

    // collect all external senders (not in our wallet list, not zero address)
    const externalSenders = new Set();

    for (const address of knownAddresses) {
        try {
            const txs = await fetchTokenTx(address, api);
            for (const tx of txs) {
                const from = tx.from.toLowerCase();
                if (!knownAddresses.includes(from) && from !== ZERO_ADDRESS) {
                    externalSenders.add(from);
                }
            }
            await sleep(200);
        } catch (e) {
            console.log(`  Error for ${address}: ${e.message}`);
        }
    }

    if (externalSenders.size === 0) {
        console.log("  No external senders found.");
        return { originTransfers: [], originWallets: [] };
    }

    console.log(`  Found ${externalSenders.size} origin wallet(s):`);
    externalSenders.forEach(a => console.log(`    ${a}`));

    // for each origin wallet, fetch their full send history
    const originTransfers = [];

    for (const sender of externalSenders) {
        console.log(`\n  Fetching all sends from ${sender.substring(0, 10)}...`);
        try {
            const txs = await fetchTokenTx(sender, api);
            for (const tx of txs) {
                originTransfers.push({
                    ...formatTx(tx),
                    isMint: tx.from === ZERO_ADDRESS
                });
            }
            await sleep(200);
        } catch (e) {
            console.log(`  Error: ${e.message}`);
        }
    }

    return { originTransfers: dedupe(originTransfers), originWallets: [...externalSenders] };
}

// -----------------------------
// Build directed graph
// -----------------------------
function buildGraph(interactions) {
    const graph = {};
    interactions.forEach(({ from, to, value, symbol, hash }) => {
        if (!graph[from]) graph[from] = [];
        graph[from].push({ to, value, symbol, hash });
    });
    return graph;
}

// -----------------------------
// DFS path finder
// -----------------------------
function findAllPaths(graph, start, end, maxDepth = 5) {
    const paths = [];
    function dfs(current, path, visited, depth) {
        if (depth > maxDepth) return;
        if (current === end && path.length > 0) { paths.push([...path]); return; }
        for (const neighbor of (graph[current] || [])) {
            if (!visited.has(neighbor.to)) {
                visited.add(neighbor.to);
                path.push({ from: current, ...neighbor });
                dfs(neighbor.to, path, visited, depth + 1);
                path.pop();
                visited.delete(neighbor.to);
            }
        }
    }
    dfs(start, [], new Set([start]), 0);
    return paths;
}

// -----------------------------
// Display helpers
// -----------------------------
function walletLabel(address) {
    const idx = wallets.findIndex(w => w.address.toLowerCase() === address.toLowerCase());
    return idx >= 0 ? `W${idx + 1}` : address.substring(0, 10) + "...";
}

function displayInteractionPaths(graph, allAddresses) {
    let found = false;
    for (let i = 0; i < allAddresses.length; i++) {
        for (let j = 0; j < allAddresses.length; j++) {
            if (i === j) continue;
            const paths = findAllPaths(graph, allAddresses[i], allAddresses[j], 5);
            if (paths.length === 0) continue;
            found = true;
            console.log(`${walletLabel(allAddresses[i])} → ${walletLabel(allAddresses[j])}: ${paths.length} path(s)`);
            paths.slice(0, 3).forEach((path, idx) => {
                const steps = path.map(s => `${walletLabel(s.from)}→${walletLabel(s.to)}`);
                console.log(`  Path ${idx + 1} (${path.length} hop${path.length > 1 ? "s" : ""}): ${steps.join(" → ")}  [${path[0].value} ${path[0].symbol}]`);
            });
            console.log();
        }
    }
    if (!found) console.log("  No paths found between these addresses.\n");
}

function displayOriginChain(originTransfers, originWallets, knownAddresses) {
    console.log("\n🌐 FULL TOKEN ORIGIN CHAIN");
    console.log("==========================\n");

    for (const origin of originWallets) {
        const sends = originTransfers.filter(t => t.from === origin || t.isMint && t.to === origin);

        // find mint (if any)
        const mint = originTransfers.find(t => t.to === origin && t.isMint);
        if (mint) {
            console.log(`  0x000...000 (mint) → ${origin.substring(0, 10)}...  [${mint.value} ${mint.symbol}]`);
        }

        console.log(`\n  Origin wallet: ${origin}`);
        console.log(`  Sent tokens to:`);

        const sentByOrigin = originTransfers.filter(t => t.from === origin);
        sentByOrigin.forEach(tx => {
            const isKnown   = knownAddresses.includes(tx.to);
            const marker    = isKnown ? " ← in your wallet list" : "";
            console.log(`    ${tx.timestamp.toISOString().replace("T", " ").substring(0, 19)}  →  ${tx.to}  [${tx.value} ${tx.symbol}]${marker}`);
        });
    }
}

// -----------------------------
// Simulation fallback (no network needed)
// -----------------------------
function runSimulation() {
    const [w1, w2, w3, w4, w5] = wallets;
    console.log("\n📊 SIMULATED INTERACTION PATHS (no real data found)");
    console.log("=====================================================");

    const sim = [
        { from: w1.address, to: w2.address, value: "0.010", symbol: "ETH" },
        { from: w2.address, to: w3.address, value: "0.005", symbol: "ETH" },
        { from: w3.address, to: w4.address, value: "0.002", symbol: "ETH" },
        { from: w2.address, to: w4.address, value: "0.003", symbol: "ETH" },
        { from: w1.address, to: w3.address, value: "0.007", symbol: "ETH" },
        { from: w3.address, to: w5.address, value: "0.004", symbol: "ETH" },
        { from: w5.address, to: w2.address, value: "0.002", symbol: "ETH" },
        { from: w4.address, to: w3.address, value: "0.001", symbol: "ETH" }
    ];

    const graph = buildGraph(sim);
    displayInteractionPaths(graph, [w1, w2, w3, w4, w5].map(w => w.address.toLowerCase()));
}

// -----------------------------
// Main
// -----------------------------
async function main() {
    console.log("🚀 INTERACTION CHAIN ANALYSER");
    console.log("==============================\n");

    console.log("Wallets loaded:");
    wallets.forEach((w, i) => {
        const label = w.privateKey === "WATCH_ONLY" ? " (watch-only)" : "";
        console.log(`  Wallet ${i + 1}: ${w.address}${label}`);
    });

    const api = getApiConfig();
    if (!api.key) {
        console.log("\n⚠️  No API key found. Running simulation only.");
        runSimulation();
        return;
    }

    // Step 1: interactions between known wallets
    const knownInteractions = await fetchKnownInteractions(api);
    const knownAddresses    = wallets.map(w => w.address.toLowerCase());

    // Step 2: trace token origins
    const { originTransfers, originWallets } = await traceOrigins(api);

    // Build combined graph (known + origin sends)
    const allTransfers = dedupe([...knownInteractions, ...originTransfers]);
    const allAddresses = [...new Set([...knownAddresses, ...originWallets])];
    const graph        = buildGraph(allTransfers);

    // Display
    if (knownInteractions.length > 0) {
        console.log(`\n✅ Found ${knownInteractions.length} interaction(s) between your wallets.\n`);
        console.log("📊 INTERACTION PATHS BETWEEN YOUR WALLETS");
        console.log("==========================================\n");
        displayInteractionPaths(buildGraph(knownInteractions), knownAddresses);
    } else {
        console.log("\n⚠️  No direct interactions found between your wallets. Showing simulation.\n");
        runSimulation();
    }

    if (originWallets.length > 0) {
        displayOriginChain(originTransfers, originWallets, knownAddresses);

        console.log("\n🔗 FULL GRAPH (origin wallets included)");
        console.log("========================================\n");
        displayInteractionPaths(graph, allAddresses);
    }

    // Save everything
    fs.writeFileSync("./interactions.json", JSON.stringify(allTransfers, null, 2));
    console.log("💾 Saved all interactions to interactions.json");
    console.log("\n✨ Analysis complete!");
}

main().catch(console.error);

// -----------------------------
// Optional: send real test transactions (requires testnet ETH)
// -----------------------------
async function sendETH(fromWallet, toAddress, amountETH) {
    try {
        const wallet = new ethers.Wallet(fromWallet.privateKey, provider);
        const tx = await wallet.sendTransaction({ to: toAddress, value: ethers.parseEther(amountETH.toString()) });
        console.log(`  Sent: ${tx.hash}`);
        await tx.wait();
        console.log(`  ✓ Confirmed`);
        return tx.hash;
    } catch (e) {
        console.log(`  ✗ Failed: ${e.message}`);
        return null;
    }
}

async function createRealInteractions() {
    console.log("💰 Sending real test transactions (requires testnet ETH)...\n");
    console.log("Step 1: Wallet 1 → Wallet 2 (0.001 ETH)");
    await sendETH(wallets[0], wallets[1].address, 0.001);
    console.log("\nStep 2: Wallet 2 → Wallet 4 (0.0005 ETH)");
    await sendETH(wallets[1], wallets[3].address, 0.0005);
    console.log("\nStep 3: Wallet 4 → Wallet 3 (0.0002 ETH)");
    await sendETH(wallets[3], wallets[2].address, 0.0002);
    console.log("\n✅ Chain complete!");
}
// createRealInteractions();
