# PT-Start-tg_bot

Этот проект представляет собой телеграм-бота, который использует Docker для удобного развертывания.

## Установка и запуск

Чтобы установить и запустить проект, выполните следующие команды:


```bash
git clone https://github.com/aerzex/PT-Start-tg_bot/
```
 Переход в директорию проекта
```bash
cd PT-Start-tg_bot/Container
```
 Запуск Docker Compose
```bash
sudo docker compose up
```
 или
```bash
sudo docker-compose up
```
## Клонирование репозитория и переход в директорию Ansible
```bas
git clone https://github.com/aerzex/PT-Start-tg_bot.git
```
```bash
cd PT-Start-tg_bot/Ansible
```
 Запуск Ansible-playbook
```bash
ansible-playbook -i inventory/hosts --extra-vars "@secrets.yml" playbook_tg_bot.yml
```
