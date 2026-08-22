# Helm EKS Deployment Debugging

## "UPGRADE FAILED: context deadline exceeded"

Helm `--wait` timed out — pods never became Ready within the timeout.

### Step 1: Enable Diagnostics (before deploying again)

Add to the pipeline's helm command:

```yaml
            --timeout 10m \
            --debug
```

Add a debug step that runs on failure:

```yaml
      - name: Debug on failure
        if: failure()
        run: |
          echo "=== PODS STATUS ==="
          kubectl get pods -n ${{ needs.setup.outputs.environment }}
          echo "=== POD DESCRIBE ==="
          kubectl describe pods -n ${{ needs.setup.outputs.environment }} -l app.kubernetes.io/name=APP_NAME
          echo "=== POD LOGS ==="
          kubectl logs -n ${{ needs.setup.outputs.environment }} -l app.kubernetes.io/name=APP_NAME --tail=100 || true
          echo "=== EVENTS ==="
          kubectl get events -n ${{ needs.setup.outputs.environment }} --sort-by='.lastTimestamp' | tail -20
```

### Step 2: Diagnose Pod State from `kubectl describe`

| Pod status column | Meaning |
|---|---|
| `0/1 Running` | Pod runs but **not Ready** → probe problem |
| `Pending` | Can't schedule → anti-affinity or resources |
| `CrashLoopBackOff` | App crashes on startup |
| `ImagePullBackOff` | Image doesn't exist or can't pull |

### Step 3: Common Causes

#### 3a. Hard PodAntiAffinity + NodeSelector

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:  # HARD — blocks if not enough nodes
```

Combined with `nodeSelector` and `replicaCount >= 2`, this **requires** N distinct nodes matching the labels. If only N-1 nodes exist, the last pod stays Pending forever.

**Fix:** Change to `preferredDuringSchedulingIgnoredDuringExecution` (soft).

#### 3b. Readiness Probe Timeout (app runs but not Ready)

**"connection refused"** → Port isn't open. App crashed or hasn't started.

**"context deadline exceeded (Client.Timeout)"** → TCP connected but HTTP didn't respond within `timeoutSeconds`.

Check what the readiness probe endpoint does:

```typescript
// If the endpoint calls an async check that can hang (DB, queue), it blocks the probe
readyRouter.get('/', async (_req, res) => {
  const dbOk = await checkDb();      // OK if quick
  const mqOk = await QueueProvider.isConnected();  // PROBLEM if it tries to connect
  res.status(dbOk ? 200 : 503).json({...});
});
```

**Fix for slow probes:** Add timeout wrapper or make checks non-blocking:

```typescript
static async isConnected(): Promise<boolean> {
  if (!this.connection) return false;  // Don't try to reconnect — instant return
  try { ... }
}
```

And set timeout on the connection itself:

```typescript
const conn = await amqp.connect(uri, { timeout: 5000 });
```

#### 3c. readOnlyRootFilesystem: true

Node.js may need to write outside mounted emptyDirs (V8 cache, temp files). Causes silent crashes.

**Fix:** Set `false` or mount additional writable volumes.

#### 3d. App crashes on DB connection failure (CrashLoopBackOff)

```typescript
try {
  await AppDataSource.initialize();
} catch (error) {
  process.exit(1);  // Pod crashes immediately
}
```

Check DB credentials (GitHub Secrets), security groups, and if the RDS endpoint resolves.

### Step 4: RabbitMQ Connectivity in EKS

**If RabbitMQ runs inside the cluster**, prefer internal DNS over external LB:

| URI | Type | Pros/Cons |
|---|---|---|
| `amqp://user:***@rabbitmq.rabbitmq.svc.cluster.local:5672/vhost` | Internal | Works from any node, no SG dependency, lower latency |
| `amqp://user:***@rabbitmq-dev.exemplo.com.br:5672/vhost` | External LB | Depends on internet route + Security Group per subnet |

**Connection timeout** (`ETIMEDOUT`) reaching external IP means the pod's subnet doesn't have a route to the RabbitMQ LB. Each EKS node is in a different subnet; a new deploy may land on a node in a subnet that wasn't previously whitelisted.

### Step 5: CI/CD Pipeline Debug Workflow

When a deploy consistently fails:

1. Add `--debug` to helm + `if: failure()` debug step
2. Check pod status: `Pending` (scheduling), `CrashLoopBackOff` (startup), or `Running 0/1` (probes)
3. Check pod logs: what does the app log at startup?
4. Check events: any `Unhealthy` probe failures?
5. Check env vars from pod describe: are secrets/configmaps propagated?

### Quick Checklist

```
[ ] --debug on helm command
[ ] if: failure() debug step in pipeline
[ ] Check pod STATUS column
[ ] Check logs for startup errors
[ ] Check probe endpoint code (does it hang?)
[ ] Check anti-affinity: required vs preferred
[ ] Check readOnlyRootFilesystem
[ ] Check nodeSelector: enough nodes with labels?
[ ] Check RabbitMQ/DB connectivity from pod's subnet
```
