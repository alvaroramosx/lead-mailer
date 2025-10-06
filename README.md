## Lead Mailer — Envío de emails personalizados desde CSV

### Descripción
Aplicación para leer un archivo CSV con contactos y datos de empresa, generar un mensaje personalizado mediante una plantilla y enviarlo por email a cada destinatario.

### Flujo de trabajo
- Coloca tu CSV en `data/contacts.csv` (o la ruta que prefieras).
- Define la plantilla del email en `templates/email.html` y, opcionalmente, el asunto en `templates/subject.txt`.
- Configura las credenciales SMTP en un archivo `.env`.
- Ejecuta el envío en modo prueba (dry-run) primero; luego realiza el envío real.

### Estructura recomendada del proyecto
- `src/` — lectura del CSV, renderizado de plantilla y envío del email
- `data/` — ficheros CSV de entrada (p. ej. `contacts.csv`)
- `templates/` — `email.html` (cuerpo) y `subject.txt` (asunto)
- `logs/` — resultados, errores y trazas de ejecución
- `.env` — variables de entorno con credenciales SMTP (no subir a Git)

### Formato del CSV
- La primera fila debe ser la cabecera.
- Codificación: UTF-8. Separador recomendado: coma (`,`) o punto y coma (`;`).
- Columnas mínimas: `nombre`, `email`, `empresa`.
- Columnas opcionales: `cargo`, `sector`, `website`, `ciudad`, `pais`, `notas`.

Ejemplo (`data/contacts.csv`):
```csv
nombre,email,empresa,cargo,sector,website
Ana Pérez,ana.perez@acme.com,Acme Corp,CMO,Tecnología,https://acme.com
Luis García,luis@contoso.es,Contoso S.A.,CEO,Servicios,https://contoso.es
```

### Variables de entorno (`.env`)
```env
SMTP_HOST=smtp.servidor.com
SMTP_PORT=587
SMTP_USER=usuario_smtp
SMTP_PASS=contraseña_smtp
SMTP_FROM="Nombre Remitente <no-reply@tu-dominio.com>"
SMTP_SECURE=false  # true para 465 (SSL), false para 587/25 (STARTTLS)

# Opcionales
RATE_LIMIT_PER_MINUTE=30   # límite de envíos por minuto
DRY_RUN=true               # true = no envía, solo simula
REPLY_TO=contacto@tu-dominio.com
```

### Plantillas
- `templates/subject.txt` (opcional): asunto del email. Permite variables.
- `templates/email.html`: cuerpo del email en HTML. Permite variables.

Variables disponibles (según columnas del CSV): `{{nombre}}`, `{{email}}`, `{{empresa}}`, `{{cargo}}`, `{{sector}}`, `{{website}}`, `{{ciudad}}`, `{{pais}}`, `{{notas}}`.

Ejemplo de `templates/subject.txt`:
```
Propuesta para {{empresa}}
```

Ejemplo de `templates/email.html`:
```html
<p>Hola {{nombre}},</p>
<p>
He revisado {{empresa}} y me llamó la atención su trabajo en el sector {{sector}}.
Me gustaría compartir una breve propuesta que podría ayudar a {{empresa}}.
</p>
<p>
¿Te parece si coordinamos una llamada esta semana?
</p>
<p>Un saludo,<br/>
Equipo de Ventas</p>
```

### Ejecución (modo sugerido)
La implementación puede ser en el lenguaje que prefieras. A continuación, dos ejemplos de ejecución esperada (elige uno):

Ejemplo con Python (sugerido):
```bash
# 1) (Opcional) Crear entorno virtual en Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate

# 2) Instalar dependencias (cuando exista requirements.txt)
pip install -r requirements.txt

# 3) Simular (dry-run)
python src/send_emails.py --csv data/contacts.csv --template templates/email.html --subject templates/subject.txt --dry-run

# 4) Envío real
python src/send_emails.py --csv data/contacts.csv --template templates/email.html --subject templates/subject.txt --rate-limit 30
```

Ejemplo con Node.js:
```bash
# 1) Instalar dependencias (cuando exista package.json)
npm install

# 2) Simular (dry-run)
node src/send-emails.mjs --csv data/contacts.csv --template templates/email.html --subject templates/subject.txt --dry-run

# 3) Envío real
node src/send-emails.mjs --csv data/contacts.csv --template templates/email.html --subject templates/subject.txt --rate-limit 30
```

Parámetros habituales (independientes del lenguaje):
- `--csv` ruta del archivo CSV.
- `--template` ruta del HTML.
- `--subject` ruta del asunto o texto literal.
- `--dry-run` no envía; registra qué ocurriría.
- `--rate-limit` límite de envíos por minuto (p. ej. 30).
- `--from` para sobrescribir `SMTP_FROM` si fuera necesario.

### Buenas prácticas y pruebas
- Usa `DRY_RUN=true` o `--dry-run` para validar plantillas y placeholders.
- Prueba en un entorno SMTP seguro (p. ej., Mailtrap) antes de enviar a producción.
- Revisa `logs/` para resultados y errores.
- Controla los reintentos y errores temporales del servidor SMTP.

### Privacidad, seguridad y cumplimiento
- No subas `data/*.csv` ni `.env` al repositorio.
- Añade un `.gitignore` con, por ejemplo:
```gitignore
.env
data/*.csv
logs/*
```
- Asegúrate de tener base legal para contactar (consentimiento/interés legítimo) y ofrece mecanismos de baja.

### Errores comunes
- Cabeceras del CSV distintas a las esperadas (p. ej., `name` en vez de `nombre`).
- Codificación no UTF-8 o separadores inconsistentes.
- Credenciales SMTP inválidas o puertos bloqueados por el firewall.

### Próximos pasos (opcional)
- Seguimiento de estado por contacto (enviado, rebotado, abierto, respondido).
- Programación de lotes y pausas automáticas para evitar límites de proveedor.
- Adjuntos opcionales o diferentes plantillas por segmento.

---
Si necesitas, puedo generar los archivos base (`src/`, script de envío, `requirements.txt` o `package.json`) para que empieces a usarlo de inmediato.


