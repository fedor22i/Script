# Script

Цей репозиторій використовує Gitleaks для перевірки секретів у коді перед комітом.

### Можливості
 * Автоматична перевірка файлів у директоріях
 * Автоматичне встановлення Gitleaks 8.27.2 для Linux/macOS/Windows

# Встановлення
1. Клонувати репозиторій

2. Запустити інсталяційний скрипт:
```
curl -fsSL https://raw.githubusercontent.com/fedor22i/Script/refs/heads/main/scripts/install.sh | bash
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

## Приклад
![Screenshot_1](https://github.com/user-attachments/assets/4e9f866f-e8db-4c27-adb9-51e2fe78ce31)
