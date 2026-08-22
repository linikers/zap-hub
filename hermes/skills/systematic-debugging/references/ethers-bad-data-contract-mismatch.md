# ethers.js BAD_DATA: Contract ABI/Bytecode Mismatch

## Error Signature

```
could not decode result data (value="0x",
  info={ "method": "owner", "signature": "owner()" },
  code=BAD_DATA, version=6.16.0)
```

Same error can appear for any function: `name()`, `symbol()`, `balanceOf()`, etc.

## Root Cause

The deployed contract at `CONTRACT_ADDRESS` **does not have the function you're calling**. The ABI in the frontend includes a function (e.g., `owner()`) that the on-chain bytecode doesn't implement — or **no contract exists at that address at all**.

## Common Scenarios

| Scenario | Why it happens | Diagnosis |
|----------|---------------|-----------|
| **No contract deployed** | Hardhat node running but `deploy` script never executed | `value="0x"` for ALL functions including `name()` |
| **Old deployment** | Updated Solidity contract but deployed address points to old bytecode | New functions fail, old ones work |
| **Wrong address** | `CONTRACT_ADDRESS` is an EOA (wallet) address, not a contract | `value="0x"` for ALL functions |
| **Wrong network** | MetaMask on Sepolia but contract is on Localhost (different address) | "connection refused" or wrong data |
| **Node restarted** | `npx hardhat node` was killed and restarted — all state lost | ALL contract state reset |
| **ABI drift** | Hand-edited ABI in `constants/index.ts` to include functions the contract doesn't have | Some functions work, others don't |

## Complete Local Development Workflow

This is the **exact sequence** to get a Hardhat + Next.js DApp running locally:

### Step 1 — Start Hardhat node (Terminal 1, keep OPEN)

```bash
cd project-root
npx hardhat node
```

⚠️ **Must stay open** — closing it destroys all contract state.

### Step 2 — Compile contracts (if changed)

```bash
npx hardhat compile
```

### Step 3 — Deploy (Terminal 2)

```bash
npx hardhat run scripts/deployTestToken.ts --network localhost
```

Expected output:
```
Deploying TestToken with the account: 0xf39Fd...
Initial supply: 1000000
TestToken deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Symbol: TTK
Total Supply: 1000000000000000000000000
```

### Step 4 — Update .env.local

```env
NEXT_PUBLIC_CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
NEXT_PUBLIC_NETWORK_NAME=Local Hardhat
NEXT_PUBLIC_CHAIN_ID=31337
```

### Step 5 — Restart frontend (Terminal 3)

```bash
cd frontend
npm run dev
```

Hard refresh with `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac).

### Step 6 — Configure MetaMask

**Add Custom Network:**
- Network Name: `Hardhat Local`
- RPC URL: `http://127.0.0.1:8545`
- Chain ID: `31337`
- Currency Symbol: `ETH`

**Import Account (MetaMask v13.31.0):**
1. Open MetaMask extension
2. Click the 3 dots (⋮) → **Settings**
3. Go to **Security & Privacy**
4. Scroll to bottom → **Import Account**
5. Paste Hardhat's first private key:
   ```
   0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
   ```

**Alternative import path:**
1. Click account name at top (pill-shaped)
2. Scroll to bottom → **Add account or hardware wallet**
3. Choose **Import Account**
4. Paste private key

**Verify:**
- Select "Hardhat Local" network
- Select imported account (`0xf39Fd...`)
- Refresh `http://localhost:3000/token`

### ⚠️ Critical Rule

**Every time you restart `npx hardhat node`, ALL state is lost.**
The sequence must be:
```
1. npx hardhat node        (Terminal 1 — stays open)
2. npx hardhat compile     (if contract changed)
3. npx hardhat run ...deploy... --network localhost  (Terminal 2)
4. npm run dev              (Terminal 3 — frontend)
```

Never restart the Hardhat node without redeploying.

## Fix

### 1. Verify the contract exists

```bash
# Check if bytecode exists at the address
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getCode","params":["0x5FbDB2315678afecb367f032d93F642f64180aa3", "latest"],"id":1}'
```

Expected: `"0x608060..."` (starts with `0x60`). If `"0x"` → no contract.

### 2. Redeploy

```bash
npx hardhat run scripts/deployTestToken.ts --network localhost
```

### 3. Update the frontend env

```env
NEXT_PUBLIC_CONTRACT_ADDRESS=0x...new_address
```

### 4. Verify

```bash
cd frontend
npm run dev
# Navigate to /admin — should no longer show BAD_DATA error
```

## Graceful Handling in Code

When calling a function that may not exist on older contract deployments:

```tsx
let owner;
try {
  owner = await contract.owner();
} catch {
  // Contract doesn't have owner() — old deployment
  setOwnerAddress(null);
  setIsOwner(null);
  return;
}
```

Then in the UI, differentiate three states:

| `isOwner` value | Meaning | UI |
|----------------|---------|-----|
| `true` | User IS the owner | Show admin forms |
| `false` | User is NOT the owner | "Access Denied" with owner address |
| `null` | Cannot determine (old contract) | "Contrato desatualizado" with redeploy instructions |

## Prevention

- After updating a Solidity contract, **always redeploy** before testing
- Use environment variables for `CONTRACT_ADDRESS` so swapping networks doesn't require code changes
- Keep the ABI in sync with the actual contract — use `hardhat typechain` to generate types
- Add a network check in the Web3Context/Provider that warns when MetaMask is on the wrong chain
