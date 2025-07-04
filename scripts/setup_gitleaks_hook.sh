#!/bin/bash

set -e

HOOK_DIR=".git/hooks"
SCRIPT_DIR="scripts"
HOOK_FILE="$HOOK_DIR/pre-commit"
PY_SCRIPT="curl -s https://raw.githubusercontent.com/fedor22i/Script/refs/heads/main/scripts/gitleaks_precommit.py | bash"

echo "Встановлення Gitleaks pre-commit hook..."

# Перевірка наявності .git
if [ ! -d "$HOOK_DIR" ]; then
    echo "Помилка: .git/hooks не знайдено. Запустіть цей скрипт у корені git-репозиторію."
    exit 1
fi

# Копіюємо hook
echo "Копіюємо pre-commit hook..."
cat > "$HOOK_FILE" <<EOF
#!/bin/bash
python3 $PY_SCRIPT
EOF

chmod +x "$HOOK_FILE"

# Даємо права на виконання Python-скрипту
chmod +x "$PY_SCRIPT"

# Вмикаємо через git config
git config gitleaks.enabled true

# Запускаємо скрипт один раз, щоб встановити gitleaks
echo "Перевірка/встановлення Gitleaks..."
python3 "$PY_SCRIPT"

echo "Gitleaks pre-commit hook успішно встановлено."
