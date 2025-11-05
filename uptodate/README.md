# UpToDate Article Scraper

Questo script scarica articoli di educazione del paziente da UpToDate per uso personale con accesso istituzionale.

## ⚠️ IMPORTANTE - Avvertenze Legali

- **Uso esclusivo personale**: Questo script è destinato SOLO per uso personale con accesso istituzionale valido
- **Non violare i termini di servizio**: UpToDate ha termini di servizio specifici che potrebbero proibire l'automazione
- **Rispetta il copyright**: Il contenuto rimane proprietà di UpToDate
- **Uso medico**: Queste informazioni non sostituiscono il parere professionale medico

## Prerequisiti

- Python 3.7+
- Accesso istituzionale valido a UpToDate
- Chrome browser installato (per Selenium)

## Installazione

1. **Installa le dipendenze Python:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Installa ChromeDriver (automatico con webdriver-manager):**
   Il driver viene scaricato automaticamente alla prima esecuzione.

## Configurazione

1. **Modifica `config.json`:**
   ```json
   {
     "username": "IL_TUO_USERNAME_ISTITUZIONALE",
     "password": "LA_TUA_PASSWORD_ISTITUZIONALE",
     "institution_login_url": "URL_DEL_LOGIN_ISTITUZIONALE",
     "delay_between_requests": 2,
     "max_retries": 3,
     "user_agent": "Mozilla/5.0 ..."
   }
   ```

2. **Trova l'URL del login istituzionale:**
   - Vai su https://www.uptodate.com
   - Clicca su "Login" o "Access through your institution"
   - Copia l'URL della pagina di login del tuo istituto

## Uso

```bash
python scraper.py
```

Lo script:
1. Si autentica tramite il portale istituzionale
2. Estrae i link degli articoli dalla sezione "Heart and Blood Vessels"
3. Scarica ogni articolo come file HTML
4. Salva tutto nella cartella `articles/`

## Struttura dei file scaricati

```
uptodate/
├── scraper.py          # Script principale
├── config.json         # Configurazione (MODIFICA QUESTO FILE)
├── requirements.txt    # Dipendenze Python
├── README.md          # Questa documentazione
└── articles/          # Articoli scaricati
    ├── articolo1.html
    ├── articolo2.html
    └── ...
```

## Personalizzazione

### Cambiare la sezione da scaricare

Modifica `self.table_of_contents_url` nello script per puntare a una sezione diversa:

```python
# Esempi di altre sezioni
self.table_of_contents_url = "https://www.uptodate.com/contents/it/table-of-contents/patient-education/diabetes-mellitus"
self.table_of_contents_url = "https://www.uptodate.com/contents/it/table-of-contents/patient-education/cancer"
```

### Modificare i selettori di autenticazione

Se il portale istituzionale ha una struttura diversa, modifica i selettori in `authenticate()`:

```python
# Adatta questi ID ai campi del tuo portale
username_field = self.driver.find_element(By.ID, "user")  # Invece di "username"
password_field = self.driver.find_element(By.ID, "pass")  # Invece di "password"
login_button = self.driver.find_element(By.ID, "submit")  # Invece di "login-button"
```

## Troubleshooting

### Errore di autenticazione
- Verifica che username/password siano corretti
- Controlla che l'URL del login istituzionale sia corretto
- Alcuni portali potrebbero richiedere autenticazione a due fattori

### ChromeDriver non trovato
- Assicurati che Chrome sia installato
- webdriver-manager dovrebbe scaricare automaticamente il driver corretto

### Articoli non trovati
- Verifica di avere accesso alla sezione italiana
- Controlla che l'URL della tabella dei contenuti sia corretto

### Blocco del sito
- Aumenta `delay_between_requests` in config.json
- Il sito potrebbe avere protezioni anti-bot

## Limitazioni

- Richiede accesso istituzionale valido
- Potrebbe non funzionare con tutti i portali di autenticazione
- Le pagine potrebbero cambiare struttura nel tempo
- Non scarica immagini o risorse esterne
- Limitato alla sezione italiana di educazione del paziente

## Supporto

Questo script è fornito "così com'è" senza garanzie. Usalo a tuo rischio.

Per problemi specifici del tuo portale istituzionale, contatta il supporto IT della tua istituzione.