# CI/CD Config Propagation Debugging

## Class of Problem

A production service is using default/fallback configuration values instead of the intended production settings. The application runs fine but a critical component (database, message queue, external service) fails to connect because it's using the wrong URL, credentials, or endpoint.

## The Investigation Chain

When a production app uses fallback config, trace backward through the deployment chain:

```
1. Application behavior
   → 2. Environment variables in the running container/pod
   → 3. Kubernetes Secret / ConfigMap
   → 4. Helm values.yaml or --set flags
   → 5. CI/CD pipeline YAML
   → 6. GitHub Secrets / AWS Secrets Manager / parameter store
```

**Test each layer. Stop at the first mismatch — that's the root cause.**

---

## Step-by-Step Diagnostic

### Step 1: Identify the Fallback

The application is using a default/fallback value. Common signs:

- Health endpoint shows `"messaging": "disconnected"` with `amqp://localhost` instead of a production URI
- Database connection points to `localhost:5432` not the RDS endpoint
- Logs show `[env] Using fallback for <VAR>` (if instrumented)
- Debug endpoints show the raw config value being used

**Check the source code** to find the fallback logic:

```ts
// Find where the config is read — the `||` is the fallback
rabbitUri: process.env.RABBIT_URI || "amqp://localhost",
```

### Step 2: Check Environment Variables in the Running Container

**Kubernetes:**
```bash
# Check env vars directly in the pod
kubectl exec -it <pod-name> -- env | grep RABBIT_URI

# Or inspect the deployment spec
kubectl get deployment <deploy-name> -o yaml | grep -A5 RABBIT_URI

# Check the Secret the deployment references
kubectl get secret <secret-name> -o yaml | grep RABBIT_URI
```

**Docker Compose:**
```bash
docker compose exec <service> env | grep RABBIT_URI
```

### Step 3: Check the Deployment Config (Helm / CloudFormation / Terraform)

**For Helm:**
```bash
# See what values were actually applied
helm get values <release-name> -n <namespace> --all

# Check what's in the values file
cat helm/<chart>/values-production.yaml | grep -A2 rabbitUri
```

Look for the exact key. Common pattern:
```yaml
secrets:
  dbUser: "real_user"        # ✅ Set
  dbPassword: "real_pass"    # ✅ Set
  rabbitUri: ""              # ❌ Empty = will be empty string in the pod
```

An empty string in Helm values creates a secret with value `""`, which causes `"" || "fallback"` to evaluate to `"fallback"` in JavaScript.

### Step 4: Check the CI/CD Pipeline

**GitHub Actions / GitLab CI / Jenkins:**
```yaml
# Find the helm upgrade/install command
- name: Deploy to EKS
  run: |
    helm upgrade --install <chart> \
      --set secrets.dbUser=${{ secrets.DB_USER }} \
      --set secrets.dbPassword=${{ secrets.DB_PASSWORD }} \
      # ❌ Missing --set secrets.rabbitUri=${{ secrets.RABBIT_URI }}
```

The missing `--set` flag propagates the empty/omitted value from `values.yaml` into production.

### Step 5: Check the Source of Truth (GitHub Secrets / AWS Secrets Manager)

```bash
# GitHub — check if the secret exists
gh secret list -R <owner/repo> | grep RABBIT_URI

# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id <name>
```

If the CI/CD pipeline doesn't have the secret, it can't set it.

---

## Common Failure Patterns

| Pattern | Diagnosis | Fix |
|---------|-----------|-----|
| **Missing `--set`** | Pipeline sets some secrets but not the new one added in `values.yaml` | Add `--set secrets.<key>=${{ secrets.<KEY> }}` in the pipeline |
| **Empty string in values.yaml** | `rabbitUri: ""` — no `--set` passed → secret has empty string | Either fill it in the values file OR always pass via CI/CD |
| **Env var mismatch** | `.env` locally has `RABBIT_URI=...` but `values.yaml` uses `rabbitUri` (different key name) | Align variable names |
| **Secret doesn't exist in CI** | Pipeline tries `${{ secrets.RABBIT_URI }}` but it wasn't created in repo settings | `gh secret set RABBIT_URI --repo owner/repo --body "value"` or create via GitHub → Settings → Secrets and variables → Actions |
| **Wrong namespace/scope** | Secret exists but is scoped to a different environment or deployment | Check environment-level secrets |
| **Helm value not referenced in template** | `--set` passes the value but the Secret template doesn't include it | Check `templates/secret.yaml` for the key |
| **PAT lacks `workflow` scope** | Push to `.github/workflows/` is rejected — `refusing to allow a Personal Access Token to create or update workflow without workflow scope` | Generate a new PAT with `workflow` scope in GitHub Settings → Developer settings → Tokens, or use `gh pr create` via API instead of git push |

## Checklist (Quick Reference)

- [ ] Application using fallback? (check logs/debug endpoints)
- [ ] Env var missing in the running container?
- [ ] Secret/ConfigMap missing or empty?
- [ ] Helm values file has empty string?
- [ ] CI/CD pipeline missing `--set` flag?
- [ ] GitHub Secret / parameter store missing the value?

## Example: Real Debug Trace

```
Symptom:  /ready shows messaging: disconnected
          /ready/queue-debug shows amqp://localhost (fallback)
Layer 1:  kubectl exec → env | grep RABBIT_URI → not set
Layer 2:  kubectl get secret → RABBIT_URI="" (empty string)
Layer 3:  helm get values → secrets.rabbitUri="" (empty in values-production.yaml)
Layer 4:  deploy.yml → helm upgrade --install has --set for dbUser/dbPassword
                      but NO --set secrets.rabbitUri
Layer 5:  GitHub Secrets → RABBIT_URI exists but never referenced in pipeline
Root:     Pipeline missing --set secrets.rabbitUri=${{ secrets.RABBIT_URI }}
Fix:      Add the missing --set flag to the helm command
```
