Para activar firma y logo en los envíos HTML:

1) Copia los ejemplos a sus nombres reales (ignorados por Git):
   - `signature.example.html` → `signature.html`
   - `logo.example.png` → `logo.png`

2) Edita `signature.html` con tus datos. El logo se referencia como `cid:logo`.

Notas:
- `signature.html` y `logo.png` están en `.gitignore` y no se subirán al repo.
- Si faltan, el envío continúa sin firma ni logo.

