import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageOps, ImageSequence

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
EXT_GIF = {".gif"}
EXT_VIDEO = {".mp4", ".mov", ".m4v", ".avi", ".webm"}

TAMANO_GRANDE = 1600
TAMANO_MINIATURA = 420
CALIDAD_GRANDE = 82
CALIDAD_MINIATURA = 75

TAMANO_GIF_GRANDE = 700
TAMANO_GIF_MINIATURA = 300

ANCHO_VIDEO = 960


def procesar_imagen(ruta_origen, ruta_destino, tamano_max, calidad):
    with Image.open(ruta_origen) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((tamano_max, tamano_max), Image.LANCZOS)
        ruta_destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(ruta_destino, "JPEG", quality=calidad, optimize=True)


def procesar_gif(ruta_origen, ruta_destino, tamano_max):
    ruta_destino.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(ruta_origen) as img:
        duracion = img.info.get("duration", 100)
        frames = []
        for frame in ImageSequence.Iterator(img):
            f = frame.convert("RGBA")
            f.thumbnail((tamano_max, tamano_max), Image.LANCZOS)
            frames.append(f)
        if frames:
            frames[0].save(
                ruta_destino,
                save_all=True,
                append_images=frames[1:],
                duration=duracion,
                loop=0,
                optimize=True,
            )


def procesar_video(ruta_origen, ruta_destino_video, ruta_destino_poster):
    ruta_destino_video.parent.mkdir(parents=True, exist_ok=True)
    ruta_destino_poster.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(ruta_origen),
            "-vf", "scale=" + str(ANCHO_VIDEO) + ":-2",
            "-c:v", "libx264", "-crf", "28", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "96k",
            str(ruta_destino_video),
        ],
        check=True,
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(ruta_origen),
            "-ss", "00:00:00.3", "-vframes", "1", "-update", "1",
            str(ruta_destino_poster),
        ],
        check=True,
    )

    with Image.open(ruta_destino_poster) as img:
        img = img.convert("RGB")
        img.thumbnail((TAMANO_MINIATURA, TAMANO_MINIATURA), Image.LANCZOS)
        img.save(ruta_destino_poster, "JPEG", quality=CALIDAD_MINIATURA, optimize=True)


def generar_html(items, titulo):
    partes = []
    for i, item in enumerate(items):
        nombre = item["nombre"]
        tipo = item["tipo"]
        ext = item["ext"]

        if tipo == "video":
            partes.append(
                '      <a href="photos/full/' + nombre + '.mp4" class="foto" data-index="'
                + str(i) + '" data-tipo="video">\n'
                + '        <img src="photos/thumb/' + nombre + '.jpg" alt="Video ' + str(i + 1) + '" loading="lazy">\n'
                + '        <span class="play">&#9658;</span>\n'
                + '      </a>'
            )
        else:
            partes.append(
                '      <a href="photos/full/' + nombre + '.' + ext + '" class="foto" data-index="'
                + str(i) + '" data-tipo="' + tipo + '">\n'
                + '        <img src="photos/thumb/' + nombre + '.' + ext + '" alt="Elemento ' + str(i + 1) + '" loading="lazy">\n'
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
    html.append('body { margin:0; min-height:100vh; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #1e3a8a, #7f1d1d) fixed; color: var(--text); }')
    html.append('header { padding: 32px 20px 12px; text-align:center; }')
    html.append('header p { opacity:0.6; margin-top:6px; font-size:14px; }')
    html.append('.grid { display:grid; gap:4px; padding:8px; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); }')
    html.append('.foto { position:relative; display:block; overflow:hidden; border-radius:6px; background: var(--card); aspect-ratio: 1/1; }')
    html.append('.foto img { width:100%; height:100%; object-fit:cover; display:block; transition: transform .3s ease; }')
    html.append('.foto:hover img { transform: scale(1.06); }')
    html.append('.play { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:26px; color:#fff; text-shadow:0 0 8px rgba(0,0,0,0.85); pointer-events:none; }')
    html.append('#lightbox { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.92); align-items:center; justify-content:center; z-index:50; flex-direction:column; }')
    html.append('#lightbox.abierto { display:flex; }')
    html.append('#lightbox-content img, #lightbox-content video { max-width:92vw; max-height:82vh; border-radius:8px; }')
    html.append('.controles { margin-top:16px; display:flex; gap:24px; }')
    html.append('.controles button { background:none; border:1px solid #555; color:var(--text); font-size:16px; padding:8px 18px; border-radius:20px; cursor:pointer; }')
    html.append('.controles button:hover { border-color: var(--accent); color: var(--accent); }')
    html.append('.cerrar { position:absolute; top:20px; right:24px; font-size:28px; cursor:pointer; }')
    html.append('.logo { max-width:180px; width:55%; height:auto; display:block; margin:0 auto; }')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<header>')
    html.append('  <img src="logo.PNG" alt="' + titulo + '" class="logo">')
    html.append('  <p>' + str(len(items)) + ' memes</p>')
    html.append('</header>')
    html.append('<div class="grid">')
    html.append(tarjetas)
    html.append('</div>')
    html.append('<div id="lightbox">')
    html.append('  <span class="cerrar" onclick="cerrar()">&times;</span>')
    html.append('  <div id="lightbox-content"></div>')
    html.append('  <div class="controles">')
    html.append('    <button onclick="mover(-1)">&larr; Anterior</button>')
    html.append('    <button onclick="mover(1)">Siguiente &rarr;</button>')
    html.append('  </div>')
    html.append('</div>')
    html.append('<script>')
    html.append("var fotos = document.querySelectorAll('.foto');")
    html.append("var lightbox = document.getElementById('lightbox');")
    html.append("var lightboxContent = document.getElementById('lightbox-content');")
    html.append('var actual = 0;')
    html.append('fotos.forEach(function(a) {')
    html.append("  a.addEventListener('click', function(e) {")
    html.append('    e.preventDefault();')
    html.append('    actual = parseInt(a.dataset.index);')
    html.append('    abrir();')
    html.append('  });')
    html.append('});')
    html.append('function abrir() {')
    html.append('  var a = fotos[actual];')
    html.append("  var tipo = a.dataset.tipo;")
    html.append("  var src = a.getAttribute('href');")
    html.append("  if (tipo === 'video') {")
    html.append('    lightboxContent.innerHTML = \'<video src="\' + src + \'" controls autoplay></video>\';')
    html.append('  } else {')
    html.append('    lightboxContent.innerHTML = \'<img src="\' + src + \'">\';')
    html.append('  }')
    html.append("  lightbox.classList.add('abierto');")
    html.append('}')
    html.append('function cerrar() {')
    html.append("  lightbox.classList.remove('abierto');")
    html.append("  lightboxContent.innerHTML = '';")
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

    todas_ext = EXT_IMAGEN | EXT_GIF | EXT_VIDEO
    archivos = []
    for p in sorted(entrada.iterdir()):
        if p.suffix.lower() in todas_ext:
            archivos.append(p)

    if not archivos:
        print("No se encontraron fotos, gifs ni videos.")
        return

    (salida / "photos" / "full").mkdir(parents=True, exist_ok=True)
    (salida / "photos" / "thumb").mkdir(parents=True, exist_ok=True)

    items = []
    for i, archivo in enumerate(archivos, 1):
        ext = archivo.suffix.lower()
        nombre_base = "item_" + str(i).zfill(4)

        if ext in EXT_IMAGEN:
            ruta_full = salida / "photos" / "full" / (nombre_base + ".jpg")
            ruta_thumb = salida / "photos" / "thumb" / (nombre_base + ".jpg")
            procesar_imagen(archivo, ruta_full, TAMANO_GRANDE, CALIDAD_GRANDE)
            procesar_imagen(archivo, ruta_thumb, TAMANO_MINIATURA, CALIDAD_MINIATURA)
            items.append({"nombre": nombre_base, "tipo": "imagen", "ext": "jpg"})

        elif ext in EXT_GIF:
            ruta_full = salida / "photos" / "full" / (nombre_base + ".gif")
            ruta_thumb = salida / "photos" / "thumb" / (nombre_base + ".gif")
            procesar_gif(archivo, ruta_full, TAMANO_GIF_GRANDE)
            procesar_gif(archivo, ruta_thumb, TAMANO_GIF_MINIATURA)
            items.append({"nombre": nombre_base, "tipo": "gif", "ext": "gif"})

        elif ext in EXT_VIDEO:
            ruta_full = salida / "photos" / "full" / (nombre_base + ".mp4")
            ruta_thumb = salida / "photos" / "thumb" / (nombre_base + ".jpg")
            procesar_video(archivo, ruta_full, ruta_thumb)
            items.append({"nombre": nombre_base, "tipo": "video", "ext": "mp4"})

        print("[" + str(i) + "/" + str(len(archivos)) + "] " + archivo.name)

    html_final = generar_html(items, args.titulo)
    (salida / "index.html").write_text(html_final, encoding="utf-8")
    (salida / ".nojekyll").write_text("")
    print("Album generado con " + str(len(archivos)) + " elementos.")


if __name__ == "__main__":
    main()
