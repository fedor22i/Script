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

![Screenshot_2](https://github.com/user-attachments/assets/23c18c09-3fa6-4f32-bc11-123f1703f2d0)
