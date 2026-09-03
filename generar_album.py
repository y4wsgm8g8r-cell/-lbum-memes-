import argparse
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
        img.save(
            ruta_destino,
            "JPEG",
            quality=calidad,
            optimize=True,
        )


def generar_html(fotos, titulo):
    partes = []
    for i, f in enumerate(fotos):
        partes.append(
            '      <a href="photos/full/' + f + '.jpg" class="foto" data-index="'
            + str(i) + '">\n'
            + '        <img src="photos/thumb/' + f + '.jpg" alt="Foto '
            + str(i + 1) + '" loading="lazy">\n'
            + '      </a>'
        )
    tarjetas = "\n".join(partes)

    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="es">')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('<title>' + titulo + '</title>')
    html.append('<style>')
    html.append(':root { --bg:#111; --card:#1b1b1b; --text:#f2f2f2; --accent:#e8b04b; }')
    html.append('* { box-sizing: border-box; }')
    html.append('body { margin:0; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); }')
    html.append('header { padding: 32px 20px 12px; text-align:center; }')
    html.append('header h1 { margin:0; font-weight:600; letter-spacing:0.5px; }')
    html.append('header p { opacity:0.6; margin-top:6px; font-size:14px; }')
    html.append('.grid { display:grid; gap:8px; padding:16px; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }')
    html.append('.foto { display:block; overflow:hidden; border-radius:10px; background: var(--card); aspect-ratio: 1/1; }')
    html.append('.foto img { width:100%; height:100%; object-fit:cover; display:block; transition: transform .3s ease; }')
    html.append('.foto:hover img { transform: scale(1.06); }')
    html.append('#lightbox { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.92); align-items:center; justify-content:center; z-index:50; flex-direction:column; }')
    html.append('#lightbox.abierto { display:flex; }')
    html.append('#lightbox img { max-width:92vw; max-height:82vh; border-radius:8px; }')
    html.append('.controles { margin-top:16px; display:flex; gap:24px; }')
    html.append('.controles button { background:none; border:1px solid #555; color:var(--text); font-size:16px; padding:8px 18px; border-radius:20px; cursor:pointer; }')
    html.append('.controles button:hover { border-color: var(--accent); color: var(--accent); }')
    html.append('.cerrar { position:absolute; top:20px; right:24px; font-size:28px; cursor:pointer; }')
    html.append('footer { text-align:center; padding:24px; opacity:0.4; font-size:12px; }')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<header>')
    html.append('  <h1>' + titulo + '</h1>')
    html.append('  <p>' + str(len(fotos)) + ' fotos</p>')
    html.append('</header>')
    html.append('<div class="grid">')
    html.append(tarjetas)
    html.append('</div>')
    html.append('<div id="lightbox">')
    html.append('  <span class="cerrar" onclick="cerrar()">&times;</span>')
    html.append('  <img id="lightbox-img" src="" alt="">')
    html.append('  <div class="controles">')
    html.append('    <button onclick="mover(-1)">&larr; Anterior</button>')
    html.append('    <button onclick="mover(1)">Siguiente &rarr;</button>')
    html.append('  </div>')
    html.append('</div>')
    html.append('<footer>Generado con Python</footer>')
    html.append('<script>')
    html.append("var fotos = document.querySelectorAll('.foto');")
    html.append("var lightbox = document.getElementById('lightbox');")
    html.append("var lightboxImg = document.getElementById('lightbox-img');")
    html.append('var actual = 0;')
    html.append('fotos.forEach(function(a) {')
    html.append("  a.addEventListener('click', function(e) {")
    html.append('    e.preventDefault();')
    html.append('    actual = parseInt(a.dataset.index);')
    html.append('    abrir();')
    html.append('  });')
    html.append('});')
    html.append('function abrir() {')
    html.append("  lightboxImg.src = fotos[actual].getAttribute('href');")
    html.append("  lightbox.classList.add('abierto');")
    html.append('}')
    html.append('function cerrar() {')
    html.append("  lightbox.classList.remove('abierto');")
    html.append('}')
    html.append('function mover(delta) {')
    html.append('  actual = (actual + delta + fotos.length) % fotos.length;')
    html.append('  abrir();')
    html.append('}')
    html.append("document.addEventListener('keydown', function(e) {")
    html.append("  if (!lightbox.classList.contains('abierto')) return;")
    html.append("  if (e.key === 'Escape') cerrar();")
    html.append("  if (e.key === 'ArrowRight') mover(1);")
    html.append("  if (e.key === 'ArrowLeft') mover(-1);")
    html.append('});')
    html.append("lightbox.addEventListener('click', function(e) {")
    html.append('  if (e.target === lightbox) cerrar();')
    html.append('});')
    html.append('</script>')
    html.append('</body>')
    html.append('</html>')

    return "\n".join(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="docs")
    parser.add_argument("--titulo", default="Mi Album de Fotos")
    args = parser.parse_args()

    entrada = Path(args.input)
    salida = Path(args.output)

    archivos = []
    for p in sorted(entrada.iterdir()):
        if p.suffix.lower() in EXTENSIONES_VALIDAS:
            archivos.append(p)

    if not archivos:
        print("No se encontraron fotos.")
        return

    (salida / "photos" / "full").mkdir(parents=True, exist_ok=True)
    (salida / "photos" / "thumb").mkdir(parents=True, exist_ok=True)

    nombres = []
    for i, archivo in enumerate(archivos, 1):
        nombre_base = "foto_" + str(i).zfill(4)
        nombres.append(nombre_base)

        ruta_full = salida / "photos" / "full" / (nombre_base + ".jpg")
        procesar_imagen(archivo, ruta_full, TAMANO_GRANDE, CALIDAD_GRANDE)

        ruta_thumb = salida / "photos" / "thumb" / (nombre_base + ".jpg")
        procesar_imagen(archivo, ruta_thumb, TAMANO_MINIATURA, CALIDAD_MINIATURA)

        print("[" + str(i) + "/" + str(len(archivos)) + "] " + archivo.name)

    html_final = generar_html(nombres, args.titulo)
    (salida / "index.html").write_text(html_final, encoding="utf-8")
    (salida / ".nojekyll").write_text("")
    print("Album generado con " + str(len(archivos)) + " fotos.")


if __name__ == "__main__":
    main()
