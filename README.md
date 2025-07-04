# Script

Цей репозиторій використовує Gitleaks для перевірки секретів у коді перед комітом.

### Можливості
 * Автоматична перевірка файлів у директоріях
 * Автоматичне встановлення Gitleaks 8.27.2 для Linux/macOS/Windows

# Встановлення
1. Клонувати репозиторій

2. Запустити інсталяційний скрипт:
```
bash scripts/setup_gitleaks_hook.sh
```

## Є можливість увімкнення/вимкнення перевірки вручну

### Увімкнути
```
git config gitleaks.enabled true
```
### Вимкнути
```
git config gitleaks.enabled false
```
## Вимоги
 * Python 3
 * curl
 * git
 * Linux/macOS/Windows (через Git Bash або WSL)

