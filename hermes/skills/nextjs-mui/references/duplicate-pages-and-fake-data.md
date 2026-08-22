# Duplicate Pages & Fake Data Patterns

## Duplicate Pages in Next.js Pages Router

Portfolio project had two perfil pages:
- `src/pages/perfil.tsx` → routed at `/perfil`
- `src/pages/perfil/perfil.tsx` → routed at `/perfil/perfil`

The second was created by accidentally putting a page inside a folder with the same name. Only one was ever used.

**Detection:**
```bash
find src/pages -name '*.tsx' -o -name '*.jsx' | sed 's|.*/||' | sort | uniq -c | sort -rn | head -20
```

Look for count > 1 on any filename.

## Fake Data in Dashboards

Dashboard had hardcoded stats:
```tsx
{["Ultimos Tweets", "Ultimos Posts Linkedin", "Ultimos PR"].map((title, index) => (
  <Typography variant="h4">{index === 0 ? "421" : index === 1 ? "408" : "802"}</Typography>
))}
```

**Fix:** Replace fake data sections with honest "Em breve" placeholder:
```tsx
<Box sx={{ textAlign: "center", py: 4, color: "text.secondary" }}>
  <Typography variant="body1">Gráficos e métricas em tempo real em breve.</Typography>
</Box>
```

**Detection:**
```bash
grep -rn '"[0-9]\{3\}"' src/pages/admin/ --include="*.tsx"
```
