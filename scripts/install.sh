#!/bin/bash
set -e

echo "Встановлення Gitleaks pre-commit hook..."

# Перевірка, що ми в git-репозиторії
if [ ! -d .git ]; then
  echo "Помилка: цей скрипт потрібно запускати в корені git-репозиторію."
  exit 1
fi

# Створення директорій
mkdir -p scripts
mkdir -p .git/hooks

# Завантаження скриптів
curl -fsSL https://raw.githubusercontent.com/fedor22i/Script/refs/heads/main/scripts/gitleaks_precommit.py -o scripts/gitleaks_precommit.py
curl -fsSL https://raw.githubusercontent.com/fedor22i/Script/refs/heads/main/scripts/pre-commit -o .git/hooks/pre-commit

# Дозволи
chmod +x scripts/gitleaks_precommit.py
chmod +x .git/hooks/pre-commit

# Вмикаємо перевірку через git config
git config gitleaks.enabled true

# Перевіряємо запуск
python scripts/gitleaks_precommit.py

echo "Gitleaks pre-commit hook встановлено успішно."
