# RabbitMQ Connectivity Diagnostics

## Class of Problem

RabbitMQ is unreachable from an application — health checks return `disconnected`, `ECONNREFUSED`, or timeout errors. Root cause could be at any layer of the network stack. Blindly changing credentials or config is guesswork.

## Step-by-Step Diagnostic (4-Layer Model)

Test each layer sequentially. Stop at the first failure — that's where the root cause lives.

```
Layer 1: URI Parse      → Is the URI format valid?
Layer 2: DNS            → Does the hostname resolve?
Layer 3: TCP            → Is the port open and reachable?
Layer 4: AMQP Handshake → Does the AMQP protocol handshake succeed?
```

---

### Layer 1: URI Parse

**What it tests:** The `RABBIT_URI` is syntactically valid.

**Common format:** `amqp://user:password@host:port/vhost`

**What can go wrong:**
- Missing scheme (`amqp://`)
- Wrong scheme (`http://`, `rabbitmq://`)
- URL-encoded credentials with special characters
- Extra whitespace or newlines in the .env value

**How to verify:**
```ts
try {
  const url = new URL(process.env.RABBIT_URI);
  console.log("Host:", url.hostname, "Port:", url.port, "Vhost:", url.pathname);
} catch (err) {
  console.error("Invalid URI:", err.message);
}
```

---

### Layer 2: DNS Resolution

**What it tests:** The hostname resolves to at least one IP address.

**How to verify (CLI):**
```bash
# Via DNS tools
nslookup rabbitmq.rabbitmq.svc.cluster.local
dig +short rabbitmq.rabbitmq.svc.cluster.local

# Via Node.js
node -e "require('dns/promises').resolve4('rabbitmq.rabbitmq.svc.cluster.local').then(console.log)"
```

**What can go wrong on Kubernetes:**
- Service name or namespace typo (`rabbitmq.rabbitmq` vs `rabbitmq.rabbitmq-system`)
- Service has no endpoints (pods not running)
- CoreDNS misconfiguration
- Service is `ExternalName` pointing to a non-existent target

**Check in Kubernetes:**
```bash
kubectl get svc -n rabbitmq
kubectl get endpoints -n rabbitmq
kubectl run -it --rm debug --image=node:20-alpine -- nslookup rabbitmq.rabbitmq.svc.cluster.local
```

---

### Layer 3: TCP Connectivity

**What it tests:** A TCP socket can connect to `host:port`.

**How to verify (CLI):**
```bash
# Via netcat
nc -zv rabbitmq.rabbitmq.svc.cluster.local 5672

# Via Node.js
node -e "
const net = require('net');
const s = net.connect(5672, 'rabbitmq.rabbitmq.svc.cluster.local', () => {
  console.log('TCP OK'); s.destroy(); process.exit(0);
});
s.on('error', (e) => { console.log('TCP FAIL:', e.message); process.exit(1); });
"
```

**What can go wrong:**
- RabbitMQ pod is not running
- Service is `ClusterIP` but accessed from outside the cluster
- NetworkPolicy or Security Group blocking the port
- Port mismatch (RabbitMQ AMQP is 5672, management UI is 15672)
- TLS termination proxy listening on a different port

**Check in Kubernetes:**
```bash
kubectl get pods -n rabbitmq -o wide
kubectl describe svc -n rabbitmq rabbitmq
kubectl run -it --rm nettest --image=alpine -- sh -c "apk add curl && curl -v telnet://rabbitmq.rabbitmq.svc.cluster.local:5672"
```

---

### Layer 4: AMQP Handshake

**What it tests:** The full AMQP protocol connection (including authentication and vhost access).

**How to verify:**
```ts
import * as amqp from "amqplib";

try {
  const conn = await amqp.connect(RABBIT_URI, { timeout: 5_000 });
  console.log("AMQP connected successfully");
  await conn.close();
} catch (err: any) {
  console.error("AMQP handshake failed:", err.message);
}
```

**Common AMQP handshake errors:**

| Error message | Root cause |
|---|---|
| `ACCESS_REFUSED - Login was refused using authentication mechanism PLAIN` | Wrong username or password |
| `access to vhost '/' refused for user 'guest'` | User doesn't have permissions on the vhost |
| `connection closed unexpectedly` | Protocol mismatch (`amqp://` vs `amqps://`), or TLS required but not used |
| `no known hosts` | DNS resolved but RabbitMQ node not part of a cluster the client can contact |
| `ENOTFOUND` | DNS failure (should have been caught at Layer 2) |
| `socket closed unexpectedly` | Server closed connection during handshake — often means wrong port (e.g. 15672 which is HTTP, not 5672) |

**Check credentials:**
```bash
# Decode the secret in Kubernetes
kubectl get secret -n taiff api-taiff-secret -o jsonpath="{.data.RABBIT_URI}" | base64 -d

# Verify the URI components:
# amqp://<user>:<password>@<host>:<port>/<vhost>
```

---

## Implementation: Diagnostic Endpoint (Express)

Add this to the health/readiness router:

```ts
import * as net from "net";
import * as dns from "dns/promises";

readyRouter.get("/queue-debug", async (_req, res) => {
  const diagnostics = { steps: [] };
  const uri = env.rabbitUri;
  const maskedUri = uri.replace(/\/\/.*@/, "//****:****@");

  // Step 1: Parse URI
  try {
    const url = new URL(uri);
    const host = url.hostname;
    const port = parseInt(url.port, 10) || 5672;
    diagnostics.steps.push({ step: 1, status: "ok", host, port });

    // Step 2: DNS
    try {
      const addrs = await dns.resolve4(host);
      diagnostics.steps.push({ step: 2, status: "ok", addresses: addrs });

      // Step 3: TCP
      try {
        await new Promise((resolve, reject) => {
          const sock = new net.Socket();
          setTimeout(() => { sock.destroy(); reject(new Error("TCP timeout")); }, 5_000);
          sock.on("connect", () => { sock.destroy(); resolve(undefined); });
          sock.on("error", reject);
          sock.connect(port, host);
        });
        diagnostics.steps.push({ step: 3, status: "ok" });

        // Step 4: AMQP (optional)
        // ... try amqp.connect(uri) ...
      } catch (e: any) {
        diagnostics.steps.push({ step: 3, status: "fail", error: e.message });
      }
    } catch (e: any) {
      diagnostics.steps.push({ step: 2, status: "fail", error: e.message });
    }
  } catch (e: any) {
    diagnostics.steps.push({ step: 1, status: "error", error: e.message });
  }

  res.json({ uri: maskedUri, ...diagnostics });
});
```

## Implementation: CLI Diagnostic Script (Node.js)

```ts
// scripts/check-rabbit.ts
import "dotenv/config";
import * as dns from "dns/promises";
import * as net from "net";
import * as amqp from "amqplib";

async function main() {
  const uri = process.env.RABBIT_URI;
  if (!uri) { console.error("RABBIT_URI not set"); process.exit(1); }

  const masked = uri.replace(/\/\/.*@/, "//****:****@");
  console.log(`Checking: ${masked}`);

  const url = new URL(uri);
  const { hostname: host, port: portStr } = url;
  const port = parseInt(portStr, 10) || 5672;

  // Layer 1: DNS
  const addrs = await dns.resolve4(host);
  console.log(`DNS OK → ${addrs.join(", ")}`);

  // Layer 2: TCP
  await new Promise((resolve, reject) => {
    const sock = new net.Socket();
    setTimeout(() => reject(new Error("TCP timeout")), 5_000);
    sock.on("connect", () => { sock.destroy(); resolve(undefined); });
    sock.on("error", reject);
    sock.connect(port, host);
  });
  console.log(`TCP OK → port ${port}`);

  // Layer 3: AMQP
  const conn = await amqp.connect(uri, { timeout: 5_000 });
  await conn.close();
  console.log("AMQP OK → RabbitMQ operational!");
}

main().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
```

## Kubernetes Checklist (when RabbitMQ is on K8s)

```bash
# 1. Is the RabbitMQ pod running?
kubectl get pods -n rabbitmq

# 2. Is the service pointing to the right pod?
kubectl get endpoints -n rabbitmq rabbitmq

# 3. Is the secret correct?
kubectl get secret -n taiff api-taiff-secret -o yaml

# 4. Does the deployment reference the right secret?
kubectl get deployment -n taiff api-taiff -o yaml | grep -A5 RABBIT

# 5. Can we connect from inside the cluster?
kubectl run -it --rm debug --image=node:20-alpine -- sh
# Inside the pod:
#   node -e "require('amqplib').connect('amqp://user:pass@rabbitmq.rabbitmq:5672/taiff').then(c => {console.log('OK'); c.close();}).catch(e => console.log('FAIL:', e.message))"

# 6. Check RabbitMQ logs
kubectl logs -n rabbitmq -l app=rabbitmq --tail=100
```

## Prevention: Connection Resilience

Once RabbitMQ is connected, add resilience to prevent future disconnections:

```ts
// Reconnection logic pattern
let retries = 0;
const MAX_RETRIES = 5;

async function connectWithRetry(): Promise<amqp.Connection> {
  while (retries < MAX_RETRIES) {
    try {
      const conn = await amqp.connect(RABBIT_URI);
      conn.on("error", (err) => console.error("[AMQP] Connection error:", err));
      conn.on("close", () => setTimeout(() => connectWithRetry(), 5_000));
      return conn;
    } catch (err) {
      retries++;
      const delay = Math.min(1000 * Math.pow(2, retries), 30_000); // exponential backoff
      console.error(`[AMQP] Connection failed (attempt ${retries}), retrying in ${delay}ms`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error("AMQP connection failed after max retries");
}
```
