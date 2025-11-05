# Configurazione DNS per benjamindeornelas.it

## ✅ Dominio configurato su Vercel

Il dominio **benjamindeornelas.it** è stato aggiunto con successo al progetto Vercel.

---

## 📋 Record DNS da configurare

Vai nel pannello del tuo **provider DNS** (dove hai registrato benjamindeornelas.it) e aggiungi questi record:

### Opzione A: Record A + CNAME (Raccomandato per compatibilità)

```
Tipo    Nome    Valore                      TTL
---------------------------------------------------
A       @       76.76.21.21                 3600
CNAME   www     cname.vercel-dns.com.       3600
```

### Opzione B: Solo CNAME (se il provider lo supporta per apex domain)

```
Tipo    Nome    Valore                      TTL
---------------------------------------------------
CNAME   @       cname.vercel-dns.com.       3600
CNAME   www     cname.vercel-dns.com.       3600
```

---

## 🔧 Istruzioni per provider comuni

### GoDaddy
1. Accedi a GoDaddy → My Products
2. Clicca su **DNS** accanto a benjamindeornelas.it
3. Aggiungi i record sopra
4. Tempo propagazione: 10-60 minuti

### Namecheap
1. Dashboard → Domain List → Manage
2. Advanced DNS
3. Aggiungi i record sopra
4. Tempo propagazione: 30 minuti - 2 ore

### Cloudflare
1. Dashboard → Select domain
2. DNS → Records → Add record
3. **IMPORTANTE**: Disabilita il proxy (cloud arancione) per i record Vercel
4. Tempo propagazione: immediata - 5 minuti

### Aruba.it
1. Pannello di controllo → Gestione DNS
2. Aggiungi record A e CNAME
3. Tempo propagazione: 2-24 ore

### Register.it
1. Area clienti → Domini → Gestione DNS
2. Aggiungi i record sopra
3. Tempo propagazione: 1-4 ore

---

## ✅ Verifica configurazione DNS

Dopo aver configurato i DNS, verifica che funzionino:

### Da terminale (Mac/Linux):

```bash
# Verifica record A
dig benjamindeornelas.it +short
# Dovrebbe mostrare: 76.76.21.21

# Verifica CNAME www
dig www.benjamindeornelas.it +short
# Dovrebbe mostrare: cname.vercel-dns.com.

# Verifica completa
nslookup benjamindeornelas.it
```

### Online:
- https://dnschecker.org/
- Cerca: benjamindeornelas.it
- Verifica che i record siano propagati globalmente

---

## 🔐 Certificato SSL

Vercel genera **automaticamente** un certificato SSL gratuito Let's Encrypt quando:
1. I record DNS sono configurati correttamente
2. La propagazione DNS è completata
3. Il dominio punta a Vercel

**Tempo generazione SSL**: 5-30 minuti dopo propagazione DNS

Puoi verificare lo stato su:
https://vercel.com/cuoreinpaces-projects/bdeornelas.github.io/settings/domains

---

## 🚀 Dopo la configurazione

Una volta che i DNS sono propagati:

1. **benjamindeornelas.it** → Sito principale
2. **www.benjamindeornelas.it** → Redirect automatico a benjamindeornelas.it
3. **HTTPS automatico** → Certificato SSL attivo

Il deploy è già completato su:
- **Temporaneo**: https://bdeornelasgithub-3kclpiezl-cuoreinpaces-projects.vercel.app
- **Produzione**: https://benjamindeornelas.it (quando DNS propagati)

---

## ⚠️ Troubleshooting

### "ERR_NAME_NOT_RESOLVED"
- DNS non ancora propagati
- Attendi 1-2 ore e riprova

### "SSL Certificate Error"
- DNS propagati ma SSL non ancora generato
- Attendi 30 minuti
- Verifica su Vercel Dashboard che il dominio sia "Active"

### "This site can't be reached"
- Record DNS errati
- Verifica che l'IP sia esattamente 76.76.21.21
- Verifica che CNAME sia cname.vercel-dns.com (con punto finale)

### Dominio non si attiva su Vercel
- Verifica che i record DNS puntino correttamente
- Rimuovi eventuali record conflittuali (altri A o CNAME per @)
- Aspetta la propagazione globale (usa dnschecker.org)

---

## 📞 Supporto

Se hai problemi:
1. Verifica DNS con `dig benjamindeornelas.it`
2. Controlla Vercel Dashboard per messaggi di errore
3. Aspetta almeno 2 ore per propagazione DNS completa

---

## 📌 Note importanti

- **NON cancellare** i record esistenti per mail/email se presenti
- Se usi email con questo dominio, mantieni i record MX
- Il redirect www → apex è automatico su Vercel
- Ogni push su main fa un nuovo deploy automatico

---

**Il sito verrà pubblicato automaticamente quando i DNS saranno propagati! 🎉**
