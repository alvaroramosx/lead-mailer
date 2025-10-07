## Lead Mailer — Envío de emails personalizados desde CSV

### Descripción
Aplicación para leer un archivo CSV con contactos y datos de empresa, generar un mensaje personalizado mediante una plantilla y enviarlo por email a cada destinatario.

### Flujo de trabajo
- Coloca tu CSV en `data/empresas.csv` con cabeceras: `Nombre,Direccion,Telefono,Web,Email,Sector,Ubicacion`.
- Define las plantillas por sector en `config/templates.yaml` (incluye una entrada `default` y el bloque `sectors`).
- Crea tu archivo `.env` a partir de `env.example` y completa las credenciales SMTP.
- Ejecuta `src/send_campaign.py` primero en modo prueba (`--dry-run`) y luego realiza el envío real.

### Estructura recomendada del proyecto
- `src/` —
  - `send_campaign.py` (parser + main; delega en `run_pipeline`)
  - `pipeline.py` (orquestación: `run_pipeline` con pasos numerados)
  - `utils.py` (helpers de contexto/normalización/formateo)
  - `templates.py` (carga y resolución de plantillas por sector)
  - `mailer.py` (construcción y envío de emails)
- `data/` — ficheros CSV de entrada (p. ej. `empresas.csv`)
- `config/` — `templates.yaml` (plantillas por sector)
- `logs/` — resultados, errores y trazas de ejecución
- `.env` — variables de entorno con credenciales SMTP (no subir a Git)

### Formato del CSV
- La primera fila debe ser la cabecera.
- Codificación: UTF-8. Separador recomendado: coma (`,`) o punto y coma (`;`).
- Columnas esperadas: `Nombre,Direccion,Telefono,Web,Email,Sector,Ubicacion`.

Ejemplo (`data/empresas.csv`):
```csv
Nombre,Direccion,Telefono,Web,Email,Sector,Ubicacion
Restaurante Mikel,"Av. Iparralde, 59, 20302 Irun, Guipúzcoa",+34 943 62 38 96,http://mikeljatetxea.com/,contacto@mikeljatetxea.com,Restaurantes,Irun
Mariño Restaurante,"Final de la calle Hirumugarrieta entrada principal Entrada secundaria, Zubelzu Kalea, 6, 20301 Irun, Gipuzkoa",+34 943 61 50 01,https://marinorestaurante.com/,info@marinorestaurante.com,Restaurantes,Irun
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

### Plantillas (YAML por sector)
- Define `config/templates.yaml` con una plantilla `default` y, opcionalmente, entradas por cada sector en `sectors`.
- Puedes usar placeholders basados en las columnas del CSV, por ejemplo `{Nombre}`, `{Email}`, `{Web}`, `{Sector}`, `{Ubicacion}`.

Ejemplo (`config/templates.yaml`):
```yaml
default:
  subject: "Consulta para {Nombre}"
  body: |
    Hola {Nombre},

    He estado revisando {Web} y me gustaría compartir una breve propuesta
    para ayudar a {Nombre} a captar más clientes en el sector {Sector}.

    ¿Te parece si coordinamos una llamada esta semana?

    Un saludo,
    Equipo Lead Mailer

sectors:
  Restaurantes:
    subject: "Mejora de visibilidad online para {Nombre}"
    body: |
      Hola {Nombre},
      Hemos ayudado a restaurantes de {Ubicacion} a incrementar reservas.
      ¿Te parece si te enseño algunos resultados y vemos si encaja para {Nombre}?

      Un saludo,
      Equipo Lead Mailer
```

### Ejecución (Windows PowerShell)
```bash
# 1) (Opcional) Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Crear tu .env a partir de env.example
copy env.example .env
# Edita .env con tus credenciales SMTP

# 4) Simular (dry-run)
python src/send_campaign.py --csv data/empresas.csv --templates config/templates.yaml --dry-run --limit 3

# 5) Envío real (con rate limit y cuerpo HTML)
python src/send_campaign.py --csv data/empresas.csv --templates config/templates.yaml --rate-limit 30 --html

# (Opcional) Solo un sector concreto
python src/send_campaign.py --csv data/empresas.csv --templates config/templates.yaml --only-sector Restaurantes --dry-run
```

Parámetros habituales:
- `--csv` ruta del archivo CSV.
- `--templates` ruta del YAML con plantillas por sector.
- `--dry-run` no envía; registra qué ocurriría.
- `--rate-limit` límite de envíos por minuto (p. ej. 30).
- `--limit` procesa solo los primeros N registros.
- `--only-sector` filtra por un sector específico.
- `--html` envía el cuerpo como HTML.

### Buenas prácticas y pruebas
- Usa `DRY_RUN=true` o `--dry-run` para validar plantillas y placeholders.
- Prueba en un entorno SMTP seguro (p. ej., Mailtrap) antes de enviar a producción.
- Revisa `logs/` para resultados y errores.
- Controla los reintentos y errores temporales del servidor SMTP.

### Arquitectura y pipeline (pasos)
- Paso 1: Cargar configuración CLI + `.env` (flags, rate-limit, SMTP, etc.).
- Paso 2: Cargar `config/templates.yaml` y resolver plantilla por `Sector` o `default`.
- Paso 3: Preparar escritura en `logs/results.csv` (cabeceras si no existe).
- Paso 4: Recorrer filas del CSV, construir contexto, previsualizar o enviar email.
- Paso 5: Mostrar resumen final por consola.

Requisito de Python: 3.10+ (se usa sintaxis de tipos `X | Y`).

### Firma y logo
- Si existen `config/signature.html` y `config/logo.png`, la firma se añade automáticamente al final del email en modo HTML y el logo se incrusta inline (CID `logo`).
- Puedes personalizar `config/signature.html` con tu información y estilos. Si no quieres firma, elimina el archivo o envía en texto plano sin `--html`.

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



