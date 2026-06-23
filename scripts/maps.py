import os
import math
import time
import zipfile
import sys
import warnings
import socket
import ssl
from io import BytesIO
from PIL import Image
import mercantile
import numpy as np
import rasterio
from rasterio.transform import from_bounds

warnings.filterwarnings("ignore")

CACHE_DIR = "tile_cache_socket"
os.makedirs(CACHE_DIR, exist_ok=True)

TILE_SIZE = 256
HOST = "pub.fgislk.gov.ru"
PORT = 443

PATH_TEMPLATE = "/plk/mapproxy-eeko/wmts/eeko-topo/webmercator/{z}/{x}/{y}.png"


def lonlat_to_mercator(lon, lat):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    y = y * 20037508.34 / 180
    return x, y


def get_bbox_from_center():
    print("\n=== УНИВЕРСАЛЬНЫЙ СКАЧИВАТЕЛЬ КАРТ ФГИС ЛК ===")
    print("Введите координаты центра и размер области в км:")
    print("Формат: широта, долгота, размер_км")
    print("Пример: 55.417644, 46.735953, 10")
    print("Для выхода введите: exit\n")
    
    while True:
        try:
            inp = input("→ ").strip()
            if inp.lower() == "exit":
                sys.exit(0)
            
            parts = [p.strip() for p in inp.replace(",", " ").split() if p.strip()]
            if len(parts) == 3:
                lat = float(parts[0])
                lon = float(parts[1])
                size_km = float(parts[2])
            elif len(parts) == 2:
                lat = float(parts[0])
                lon = float(parts[1])
                size_km = 10.0
            else:
                raise ValueError("Неверное количество параметров.")
                
            size_km = max(0.5, min(40, size_km))
            
            deg_per_km_lat = 1 / 111.0                    
            deg_per_km_lon = 1 / (111.0 * math.cos(math.radians(lat)))  
            
            size_deg_lat = size_km * deg_per_km_lat
            size_deg_lon = size_km * deg_per_km_lon
            
            min_lon = lon - (size_deg_lon / 2)
            max_lon = lon + (size_deg_lon / 2)
            min_lat = lat - (size_deg_lat / 2)
            max_lat = lat + (size_deg_lat / 2)
            
            print(f"✅ Координаты: {lat:.6f}, {lon:.6f} | Охват: {size_km} км")
            return min_lon, min_lat, max_lon, max_lat
            
        except Exception as e:
            print(f"❌ Ошибка ввода: {e}. Попробуйте ещё раз.\n")


def download_tile_via_socket(z, x, y):
    path = f"{CACHE_DIR}/{z}_{x}_{y}.png"
    if os.path.exists(path) and os.path.getsize(path) > 500:
        try:
            return Image.open(path).convert("RGBA")
        except:
            pass

    tile_path = PATH_TEMPLATE.format(z=z, x=x, y=y)
    
    http_request = (
        f"GET {tile_path} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        f"Accept: image/avif,image/webp,image/png,image/*\r\n"
        f"Connection: close\r\n\r\n"
    ).encode('utf-8')

    context = ssl._create_unverified_context()
    
    for attempt in range(3):
        try:
            sock = socket.create_connection((HOST, PORT), timeout=8)
            secure_sock = context.wrap_socket(sock, server_hostname=HOST)
            secure_sock.sendall(http_request)
            
            response = b""
            headers_ended = False
            content_length = None
            body = b""
            
            while not headers_ended:
                chunk = secure_sock.recv(1024)
                if not chunk:
                    break
                response += chunk
                if b"\r\n\r\n" in response:
                    headers_ended = True
                    headers_part, body_part = response.split(b"\r\n\r\n", 1)
                    header_str = headers_part.decode('utf-8', errors='ignore')
                    body = body_part
                    
                    for line in header_str.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            content_length = int(line.split(":")[1].strip())
                            break
            
            if content_length is not None:
                while len(body) < content_length:
                    needed = content_length - len(body)
                    data = secure_sock.recv(min(4096, needed))
                    if not data:
                        break
                    body += data
            else:
                while True:
                    data = secure_sock.recv(4096)
                    if not data:
                        break
                    body += data
                    
            secure_sock.close()
            
            if "200 OK" in header_str and len(body) > 400:
                img = Image.open(BytesIO(body)).convert("RGBA")
                img.save(path)
                return img
            elif "404 Not Found" in header_str:
                return Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
                
        except:
            time.sleep(0.2)
            
    return Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))


def stitch(bounds, z, coords):
    x_min, x_max, y_min, y_max = bounds
    width = (x_max - x_min + 1) * TILE_SIZE
    height = (y_max - y_min + 1) * TILE_SIZE

    print("🧩 Склеивание фрагментов на белую подложку...")
    rgba_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    for x, y in coords:
        path = f"{CACHE_DIR}/{z}_{x}_{y}.png"
        if os.path.exists(path):
            try:
                tile = Image.open(path).convert("RGBA")
                px = (x - x_min) * TILE_SIZE
                py = (y - y_min) * TILE_SIZE
                rgba_layer.paste(tile, (px, py), tile)
            except:
                pass

    bg_white = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    final_img = Image.alpha_composite(bg_white, rgba_layer)
    return final_img.convert("RGB")


def get_geo_bounds(z, bounds):
    x_min, x_max, y_min, y_max = bounds
    ul_tile = mercantile.bounds(x_min, y_min, z)
    lr_tile = mercantile.bounds(x_max, y_max, z)
    return ul_tile.west, lr_tile.south, lr_tile.east, ul_tile.north


# ИСПРАВЛЕНО ДЛЯ MARBLE: Прописываем абсолютный системный путь к файлу result.png
def export_pure_kml(west, south, east, north):
    print("📝 ГИС-Экспорт: Создание result.kml с абсолютным путем для Marble...")
    
    abs_path_to_png = os.path.abspath("result.png")
    
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://opengis.net">
  <Folder>
    <name>FGIS LK Complete Map</name>
    <GroundOverlay>
      <name>Forest and Roads Layer</name>
      <Icon><href>{abs_path_to_png}</href></Icon>
      <LatLonBox>
        <north>{north}</north>
        <south>{south}</south>
        <east>{east}</east>
        <west>{west}</west>
      </LatLonBox>
    </GroundOverlay>
  </Folder>
</kml>"""
    with open("result.kml", "w", encoding="utf-8") as f:
        f.write(kml_content)


def export_kmz(west, south, east, north):
    print("📦 ГИС-Экспорт: Упаковка в result.kmz для Garmin BaseCamp...")
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://opengis.net">
  <Folder>
    <name>FGIS LK BaseCamp</name>
    <GroundOverlay>
      <name>Forest Map Layer</name>
      <Icon><href>result.png</href></Icon>
      <LatLonBox>
        <north>{north}</north>
        <south>{south}</south>
        <east>{east}</east>
        <west>{west}</west>
      </LatLonBox>
    </GroundOverlay>
  </Folder>
</kml>"""
    with zipfile.ZipFile("result.kmz", "w", zipfile.ZIP_STORED) as kmz:
        kmz.writestr("doc.kml", kml_content)
        kmz.write("result.png", "result.png")




import sqlite3

def export_osmand_sqlite(bounds, z, coords):
    print("📦 ГИС-Экспорт: Создание карты по строгому стандарту OsmAnd SQLite...")
    db_path = "fgis_les.sqlitedb"
    
    # Удаляем старый файл, если он остался, чтобы избежать конфликтов
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Создаем основные таблицы
    cur.execute("CREATE TABLE tiles (x INTEGER, y INTEGER, z INTEGER, image BLOB, tags TEXT);")
    cur.execute("CREATE INDEX IND on tiles (x,y,z);")
    
    # КРИТИЧЕСКИ ВАЖНО ДЛЯ OSMAND: В таблице info колонки ДОЛЖНЫ быть БЕЗ указания типов данных!
    # Иначе OsmAnd не сможет прочитать minzoom/maxzoom и сбросит карту на 500 км.
    cur.execute("""
        CREATE TABLE info (
            tilenumbering, minzoom, maxzoom, url, rule, 
            referer, ellipsoid, inverted_y, expireminutes, randoms
        );
    """)
    
    # Прописываем лимиты (разрешаем растягивать карту на любой масштаб от 1 до 22)
    cur.execute("""
        INSERT INTO info (tilenumbering, minzoom, maxzoom, inverted_y) 
        VALUES ('simple', 1, 22, 'false');
    """)
    
    count = 0
    for x, y in coords:
        path = f"{CACHE_DIR}/{z}_{x}_{y}.png"
        if os.path.exists(path):
            with open(path, "rb") as f:
                tile_bytes = f.read()
            
            # Записываем тайл
            cur.execute(
                "INSERT INTO tiles (x, y, z, image) VALUES (?, ?, ?, ?);",
                (x, y, z, sqlite3.Binary(tile_bytes))
            )
            count += 1
            
    conn.commit()
    conn.close()
    print(f"🎉 Карта успешно скомпилирована в файл: {db_path}")



def export_geotiff(img, z, bounds):
    print("🌍 ГИС-Экспорт: Запись привязки в result.tif...")
    x_min, x_max, y_min, y_max = bounds
    ul_bounds = mercantile.xy_bounds(x_min, y_min, z)
    lr_bounds = mercantile.xy_bounds(x_max, y_max, z)
    
    transform = from_bounds(ul_bounds.left, lr_bounds.bottom, lr_bounds.right, ul_bounds.top, img.width, img.height)
    arr = np.array(img)

    with rasterio.open(
        "result.tif", "w", driver="GTiff",
        height=img.height, width=img.width, count=3,
        dtype=arr.dtype, crs="EPSG:3857", transform=transform,
        compress="deflate", predictor=2
    ) as dst:
        for i in range(3):
            dst.write(arr[:, :, i], i + 1)


def main():
    min_lon, min_lat, max_lon, max_lat = get_bbox_from_center()
    z = 15               
    
    tmin = mercantile.tile(min_lon, max_lat, z)
    tmax = mercantile.tile(max_lon, min_lat, z)
    x_min, x_max, y_min, y_max = tmin.x, tmax.x, tmin.y, tmax.y
    
    bounds = (x_min, x_max, y_min, y_max)
    coords = [(x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1)]
    total = len(coords)
    
    print(f"📡 Масштаб (Zoom): {z} | Всего тайлов для проверки: {total}")
    
    count = 0
    for x, y in coords:
        download_tile_via_socket(z, x, y)
        count += 1
        if count % 10 == 0 or count == total:
            print(f"⏳ Загружено: {count}/{total} тайлов...")
            
    img = stitch(bounds, z, coords)
    img.save("result.png")
    print("✅ Базовый растр result.png успешно сформировован.")
    
    west, south, east, north = get_geo_bounds(z, bounds)
    
    export_pure_kml(west, south, east, north)
    export_kmz(west, south, east, north)
    export_geotiff(img, z, bounds)
    export_osmand_sqlite(bounds, z, coords)
    
    print("\n🏁 ВСЕ ФАЙЛЫ УСПЕШНО СГЕНЕРИРОВАНЫ!")
    print("-> Для Marble откройте файл: 'result.kml'")
    print("-> Для BaseCamp откройте файл: 'result.kmz'")
    print("-> Для QGIS откройте файл: 'result.tif'")


if __name__ == "__main__":
    main()
