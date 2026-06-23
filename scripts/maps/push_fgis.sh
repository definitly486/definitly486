#!/bin/sh

SOURCE_DIR="$HOME/result_output"
TARGET_DIR="/storage/emulated/0/Android/data/net.osmand/files/tiles"

# Проверка файлов
FILES=$(ls "$SOURCE_DIR"/*.sqlitedb 2>/dev/null)

if [ -z "$FILES" ]; then
    echo "❌ Нет .sqlitedb файлов в $SOURCE_DIR"
    exit 1
fi

# adb
adb start-server > /dev/null

DEVICE=$(adb devices | awk 'NR>1 && $2=="device" {print $1}' | head -n 1)

if [ -z "$DEVICE" ]; then
    echo "❌ Устройство не найдено или не авторизовано"
    exit 1
fi

echo "✅ Устройство: $DEVICE"

adb shell "mkdir -p $TARGET_DIR"

echo "📤 Загружаю все sqlitedb файлы..."

for FILE in $FILES; do
    echo "→ $FILE"
    adb push "$FILE" "$TARGET_DIR/"
done

echo "✅ Готово: все sqlitedb загружены"