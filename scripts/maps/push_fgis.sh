#!/bin/sh

FILE="$HOME/result_output/fgis_les.sqlitedb"
TARGET_DIR="/storage/emulated/0/Android/data/net.osmand/files/tiles"

# Проверка файла
if [ ! -f "$FILE" ]; then
    echo "❌ Файл $FILE не найден в текущей папке"
    exit 1
fi

# Проверка подключения устройства
DEVICE=$(adb devices | grep -w "device" | awk '{print $1}' | head -n 1)

if [ -z "$DEVICE" ]; then
    echo "❌ Устройство не найдено"
    exit 1
fi

echo "✅ Устройство найдено: $DEVICE"

# Проверка доступа к ADB
adb start-server > /dev/null

# Проверка авторизации
STATE=$(adb devices | grep "$DEVICE" | awk '{print $2}')

if [ "$STATE" != "device" ]; then
    echo "❌ Устройство не авторизовано (проверь USB debugging)"
    exit 1
fi

echo "📤 Копирование файла..."

adb push "$FILE" "$TARGET_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ Файл успешно загружен в $TARGET_DIR"
else
    echo "❌ Ошибка при копировании"
fi