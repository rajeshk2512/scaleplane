#!/usr/bin/env bash
# Generate SDK models from the committed OpenAPI snapshot.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OPENAPI="$ROOT/sdks/openapi/scaleplane.openapi.json"

if [[ ! -f "$OPENAPI" ]]; then
  echo "Missing OpenAPI snapshot. Run: make sdk-export" >&2
  exit 1
fi

echo "==> Python models (datamodel-code-generator)"
PYTHON_BIN="${SCALEPLANE_PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
    PYTHON_BIN="$ROOT/backend/.venv/bin/python"
  else
    PYTHON_BIN="python3"
  fi
fi
"$PYTHON_BIN" -m pip install -q "datamodel-code-generator>=0.26.0"
"$PYTHON_BIN" -m datamodel_code_generator \
  --input "$OPENAPI" \
  --input-file-type openapi \
  --output "$ROOT/sdks/python/src/scaleplane/_generated/models.py" \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.12 \
  --use-standard-collections \
  --use-union-operator \
  --collapse-root-models \
  --field-constraints \
  --snake-case-field \
  --capitalise-enum-members

mkdir -p "$ROOT/sdks/python/src/scaleplane/_generated"
touch "$ROOT/sdks/python/src/scaleplane/_generated/__init__.py"

echo "==> TypeScript types (openapi-typescript)"
(
  cd "$ROOT/sdks/typescript"
  if [[ ! -d node_modules ]]; then
    npm install
  fi
  npx openapi-typescript "$OPENAPI" -o src/generated/schema.ts
)

echo "==> Java models (openapi-generator)"
if [[ -z "${JAVA_HOME:-}" ]]; then
  if [[ -d /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home ]]; then
    export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
    export PATH="$JAVA_HOME/bin:$PATH"
  fi
fi

JAVA_OUT="$ROOT/sdks/java/src/main/java/com/scaleplane/generated"
TMP_JAVA="$(mktemp -d)"
trap 'rm -rf "$TMP_JAVA"' EXIT

npx --yes @openapitools/openapi-generator-cli generate \
  -i "$OPENAPI" \
  -g java \
  -o "$TMP_JAVA" \
  --global-property models,modelTests=false,modelDocs=false,supportingFiles=false \
  --additional-properties=library=native,serializationLibrary=jackson,dateLibrary=java8,useJakartaEe=true,modelPackage=com.scaleplane.generated,hideGenerationTimestamp=true,openApiNullable=false,useBeanValidation=false

rm -rf "$JAVA_OUT"
mkdir -p "$JAVA_OUT"
cp -R "$TMP_JAVA/src/main/java/com/scaleplane/generated/." "$JAVA_OUT/"

# Drop models that require skipped AbstractOpenApiSchema (unused by runtime SDK).
rm -f "$JAVA_OUT/LocationInner.java" \
      "$JAVA_OUT/ValidationError.java" \
      "$JAVA_OUT/HTTPValidationError.java"

echo "SDK model generation complete."
