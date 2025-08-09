#!/bin/bash

# Путь к исходным proto-файлам в проекте бэкенд-сервиса
PROTO_SRC_DIR="../game_userver/proto"

# Директория для сгенерированного Python-кода внутри проекта бота
PROTO_GEN_DIR="./game_bot/proto"

# 1. Очищаем и создаем директорию для сгенерированных файлов
echo "Cleaning up previous generated files..."
rm -rf "${PROTO_GEN_DIR}"
mkdir -p "${PROTO_GEN_DIR}"

# 2. Находим все .proto файлы в исходной директории
PROTO_FILES=$(find "${PROTO_SRC_DIR}" -name "*.proto")

if [ -z "$PROTO_FILES" ]; then
    echo "No .proto files found in ${PROTO_SRC_DIR}"
    exit 1
fi

echo "Found proto files:"
echo "$PROTO_FILES"
echo ""

# 3. Генерируем Python gRPC код
# -I (include) указывает, где искать импортируемые .proto файлы.
# --python_out и --grpc_python_out указывают, куда складывать сгенерированный код.
# protoc сохранит структуру директорий относительно пути -I.
echo "Generating Python gRPC code..."
python3 -m grpc_tools.protoc \
  -I"${PROTO_SRC_DIR}" \
  --python_out="${PROTO_GEN_DIR}" \
  --grpc_python_out="${PROTO_GEN_DIR}" \
  $PROTO_FILES

# Проверяем успешность генерации
if [ $? -ne 0 ]; then
    echo "Proto generation failed!"
    exit 1
fi

# 4. Исправляем импорты в сгенерированных файлах, делая их относительными
# Это необходимо, потому что protoc генерирует абсолютные импорты
echo "Fixing imports in generated files..."
find "${PROTO_GEN_DIR}" -name "*_pb2.py" -exec sed -i -E 's/^import (models|handlers)\.(.*_pb2)/from . import \2/g' {} \;
find "${PROTO_GEN_DIR}" -name "*_pb2_grpc.py" -exec sed -i -E 's/^import (models|handlers)\.(.*_pb2)/from . import \2/g' {} \;

# 5. Создаем __init__.py файлы, чтобы сделать директории Python-пакетами
echo "Creating __init__.py files..."
# Создаем __init__.py во всех директориях, включая корневую
touch "${PROTO_GEN_DIR}/__init__.py"
find "${PROTO_GEN_DIR}" -mindepth 1 -type d -exec touch {}/__init__.py \;


echo ""
echo "Proto generation successful!"
echo "Generated files are in ${PROTO_GEN_DIR}"
echo "You can now import them in your bot, e.g.: from game_bot.proto.handlers import cruds_pb2"