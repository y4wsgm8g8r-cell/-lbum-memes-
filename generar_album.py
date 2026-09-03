import argparse
import os
import shutil
from pathlib import Path
from PIL import Image, ImageOps

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
TAMANO_GRANDE = 1600
TAMANO_MINIATURA = 420
CALIDAD_GRANDE = 82
CALIDAD_MINIATURA = 75


def procesar_imagen(ruta_origen, ruta_destino, tamano_max, calidad):
    with Image.open(ruta_origen) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((tamano_max, tamano_max), Image.LANCZOS)
        ruta_destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(ruta_destino, "JPEG", quality=calidad, optimize=True)


def generar_html(fotos, titulo):
    tarjetas = "\n".join(
        f'''      <a href="photos/full/{f}.jpg" class="foto" data-index="{i}">
        <img src="photos/thumb/{f}.jpg" alt="Foto {i+1}" loading="lazy">
      </a>'''
        for i, f in enumerate(fotos)
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<style>
  :root {{ --bg:#111; --card:#1b1b1b; --text:#f2f2f2; --accent:#e8b04b; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); }}
  header {{ padding: 32px 20px 12px; text-align:center; }}
  header h1 {{ margin:0; font-weight:600; letter-spacing:0.5px; }}
  header p {{ opacity:0.6; margin-top:6px; font-size:14px; }}
  .grid {{ display:grid; gap:8px; padding:16px; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }}
  .foto {{ display:block; overflow:hidden; border-radius:10px; background: var(--card); aspect-ratio: 1/1; }}
  .foto img {{ width:100%; height:100%; object-fit:cover; display:block; transition: transform .3s ease; }}
  .foto:hover img {{ transform: scale(1.06); }}
  #lightbox {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.92); align-items:center; justify-content:center; z-index:50; flex-direction:column; }}
  #lightbox.abierto {{ display:flex; }}
  #lightbox img {{ max-width:92vw; max-height:82vh; border-radius:8px; }}
  .controles {{ margin-top:16px; display:flex; gap:24px; }}
  .controles button {{ background:none; border:1px solid #555; color:var(--text); font-size:16px; padding:8px 18px; border-radius:20px; cursor:pointer; }}
  .controles button:hover {{ border-color: var(--accent); color: var(--accent); }}
  .cerrar {{ position:absolute; top:20px; right:24px; font-size:28px; cursor:pointer; }}
  footer {{ text-align:center; padding:24px; opacity:0.4; font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>{titulo}</h1>
  <p>{len(fotos)} fotos</p>
</header>
<div class="grid">
{tarjetas}
</div>
<div id="lightbox">
  <span class="cerrar" onclick="cerrar()">&times;</span>
  <img id="lightbox-img" src="" alt="">
  <div class="controles">
    <button onclick="mover(-1)">&larr; Anterior</button>
    <button onclick="mover(1)">Siguiente &rarr;</button>
  </div>
</div>
<footer>Generado con Python · GitHub Pages</footer>
<script>
  const fotos = document.querySelectorAll('.foto');
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  let actual = 0;
  fotos.forEach(a => a.addEventListener('click', e => {{
    e.preventDefault();
    actual = parseInt(a.dataset.index);
    abrir();
  }}));
  function abrir() {{
    lightboxImg.src = fotos[actual].getAttribute('href');
    lightbox.classList.add('abierto');
  }}
  function cerrar() {{ lightbox.classList.remove('abierto'); }}
  function mover(delta) {{
    actual = (actual + delta + fotos.length) % fotos.length;
    abrir();
  }}
  document.addEventListener('keydown', e => {{
    if (!lightbox.classList.contains('abierto')) return;
    if (e.key === 'Escape') cerrar();
    if (e.key === 'ArrowRight') mover(1);
    if (e.key === 'ArrowLeft') mover(-1);
  }});
  lightbox.addEventListener('click', e => {{ if (e.target === lightbox) cerrar(); }});
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="docs")
    parser.add_argument("--titulo", default="Mi Álbum de Fotos")
    args = parser.parse_args()

    entrada = Path(args.input)
    salida = Path(args.output)

    archivos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in EXTENSIONES_VALIDAS)
    if not archivos:
        print("No se encontraron fotos.")
        return

    (salida / "photos" / "full").mkdir(parents=True, exist_ok=True)
    (salida / "photos" / "thumb").mkdir(parents=True, exist_ok=True)

    nombres = []
    for i, archivo in enumerate(archivos, 1):
        nombre_base = f"foto_{i:04d}"
        nombres.append(nombre_base)
        procesar_imagen(archivo, salida / "photos" / "full" / f"{nombre_base}.jpg", TAMANO_GRANDE, C
