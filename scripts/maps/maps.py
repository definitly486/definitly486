import os
import math
import socket
import ssl
import sqlite3
from io import BytesIO
from PIL import Image
import mercantile
import rasterio
from rasterio.transform import from_bounds
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# PATHS
# -----------------------------
OUTPUT_DIR = "result_output"
CACHE_DIR = os.path.join(OUTPUT_DIR, "tile_cache_socket")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

TILE_SIZE = 256
HOST = "pub.fgislk.gov.ru"
PORT = 443

PATH_TEMPLATE = "/plk/mapproxy-eeko/wmts/eeko-topo/webmercator/{z}/{x}/{y}.png"


# -----------------------------
# INPUT
# -----------------------------
def get_bbox():
    print("lat lon size_km")
    lat, lon, size_km = map(float, input("→ ").replace(",", " ").split())

    dlat = size_km / 111.0
    dlon = size_km / (111.0 * math.cos(math.radians(lat)))

    return lon - dlon/2, lat - dlat/2, lon + dlon/2, lat + dlat/2


# -----------------------------
# TILE DOWNLOAD (FIX BLACK TILES)
# -----------------------------
def download_tile(z, x, y):
    path = f"{CACHE_DIR}/{z}_{x}_{y}.png"

    if os.path.exists(path):
        try:
            return Image.open(path).convert("RGBA")
        except:
            pass

    req = (
        f"GET {PATH_TEMPLATE.format(z=z,x=x,y=y)} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"User-Agent: Mozilla/5.0\r\n"
        f"Connection: close\r\n\r\n"
    ).encode()

    ctx = ssl._create_unverified_context()

    try:
        sock = socket.create_connection((HOST, PORT), timeout=10)
        s = ctx.wrap_socket(sock, server_hostname=HOST)
        s.sendall(req)

        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk

        s.close()

        header, body = data.split(b"\r\n\r\n", 1)

        if b"200 OK" not in header:
            return None

        img = Image.open(BytesIO(body)).convert("RGBA")

        # 🔥 FIX: real empty tile detection (not getextrema bug)
        if img.getbbox() is None:
            return None

        img.save(path)
        return img

    except:
        return None


# -----------------------------
# TILE MATRIX (XYZ CLEAN)
# -----------------------------
def build_tiles(min_lon, min_lat, max_lon, max_lat, zooms):
    out = {}

    for z in zooms:

        tiles = list(mercantile.tiles(min_lon, min_lat, max_lon, max_lat, [z]))

        xs = [t.x for t in tiles]
        ys = [t.y for t in tiles]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        coords = [
            (x, y)
            for x in range(x_min, x_max + 1)
            for y in range(y_min, y_max + 1)
        ]

        out[z] = coords

    return out


# -----------------------------
# STITCH (NO BLACK AREAS)
# -----------------------------
def stitch(z, coords):
    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]

    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    canvas = Image.new(
        "RGBA",
        ((x_max - x_min + 1) * TILE_SIZE,
         (y_max - y_min + 1) * TILE_SIZE),
        (255, 255, 255, 255)
    )

    for x, y in coords:
        path = f"{CACHE_DIR}/{z}_{x}_{y}.png"

        if not os.path.exists(path):
            continue

        tile = Image.open(path).convert("RGBA")

        # 🔥 FIX: skip fully transparent tiles
        if tile.getbbox() is None:
            continue

        px = (x - x_min) * TILE_SIZE
        py = (y - y_min) * TILE_SIZE

        canvas.paste(tile, (px, py), tile)

    return canvas.convert("RGB")


# -----------------------------
# OSMAND SQLITEDB (FIXED FINAL)
# -----------------------------
def export_sqlitedb(all_tiles):
    db = os.path.join(OUTPUT_DIR, "fgis_les.sqlitedb")

    if os.path.exists(db):
        os.remove(db)

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE tiles (
            x INTEGER,
            y INTEGER,
            z INTEGER,
            image BLOB
        );
    """)

    cur.execute("CREATE INDEX idx ON tiles(x,y,z);")

    cur.execute("""
        CREATE TABLE info (
            tilenumbering TEXT,
            minzoom INTEGER,
            maxzoom INTEGER,
            inverted_y INTEGER
        );
    """)

    minz = min(all_tiles.keys())
    maxz = max(all_tiles.keys())

    # 🔥 IMPORTANT: XYZ MODE (NO FLIP IN DB)
    cur.execute("INSERT INTO info VALUES ('xyz', ?, ?, 0);", (minz, maxz))

    total = 0

    for z, coords in all_tiles.items():
        for x, y in coords:

            path = f"{CACHE_DIR}/{z}_{x}_{y}.png"

            if not os.path.exists(path):
                continue

            with open(path, "rb") as f:
                data = f.read()

            cur.execute(
                "INSERT INTO tiles VALUES (?,?,?,?)",
                (x, y, z, sqlite3.Binary(data))
            )

            total += 1

    conn.commit()
    conn.close()

    print("SQLITEDB OK:", total)


# -----------------------------
# MBTILES (ONLY HERE TMS FLIP)
# -----------------------------
def export_mbtiles(all_tiles):
    path = os.path.join(OUTPUT_DIR, "fgis_les.mbtiles")

    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()

    cur.execute("CREATE TABLE metadata (name TEXT, value TEXT);")

    cur.execute("""
        CREATE TABLE tiles (
            zoom_level INTEGER,
            tile_column INTEGER,
            tile_row INTEGER,
            tile_data BLOB
        );
    """)

    for z, coords in all_tiles.items():
        max_tile = (1 << z) - 1

        for x, y in coords:

            path = f"{CACHE_DIR}/{z}_{x}_{y}.png"

            if not os.path.exists(path):
                continue

            with open(path, "rb") as f:
                data = f.read()

            # 🔥 ONLY MBTILES uses TMS flip
            tms_y = max_tile - y

            cur.execute(
                "INSERT INTO tiles VALUES (?,?,?,?)",
                (z, x, tms_y, sqlite3.Binary(data))
            )

    conn.commit()
    conn.close()

    print("MBTiles OK")


def export_geotiff(all_tiles, min_lon, min_lat, max_lon, max_lat, z):
    import numpy as np

    img = stitch(z, all_tiles[z])  # уже RGB PIL image
    arr = np.array(img)

    height, width = arr.shape[:2]

    # трансформация из bbox → пиксели
    transform = from_bounds(
        min_lon, min_lat,
        max_lon, max_lat,
        width,
        height
    )

    tif_path = os.path.join(OUTPUT_DIR, "result.tif")

    with rasterio.open(
    tif_path,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=arr.dtype,
    crs="EPSG:3857",
    transform=transform,
    compress="LZW",
    tiled=True,
    blockxsize=256,
    blockysize=256,
    photometric="RGB",
    ) as dst:
        dst.write(arr[:, :, 0], 1)  # R
        dst.write(arr[:, :, 1], 2)  # G
        dst.write(arr[:, :, 2], 3)  # B

    print("GeoTIFF OK →", tif_path)



def download_worker(task):
    z, x, y = task
    download_tile(z, x, y)


# -----------------------------
# MAIN
# -----------------------------
def main():
    min_lon, min_lat, max_lon, max_lat = get_bbox()

    zooms = list(range(6, 16))

    all_tiles = build_tiles(min_lon, min_lat, max_lon, max_lat, zooms)

    
    # DOWNLOAD (THREADS)
    tasks = [
    (z, x, y)
    for z in zooms
    for x, y in all_tiles[z]
    ]

    print("TOTAL TILES:", len(tasks))

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(download_worker, t) for t in tasks]

    for i, f in enumerate(as_completed(futures), 1):
        try:
            f.result()
        except:
            pass

        if i % 500 == 0:
            print(f"downloaded {i}/{len(tasks)}")

    # STITCH LAST ZOOM
    z = zooms[-1]
    img = stitch(z, all_tiles[z])

    img.save(os.path.join(OUTPUT_DIR, "result.png"))

    export_sqlitedb(all_tiles)
    export_mbtiles(all_tiles)

    print("DONE →", OUTPUT_DIR)

    z = zooms[-1]
    img = stitch(z, all_tiles[z])

    img.save(os.path.join(OUTPUT_DIR, "result.png"))

    export_geotiff(all_tiles, min_lon, min_lat, max_lon, max_lat, z)

if __name__ == "__main__":
    main()