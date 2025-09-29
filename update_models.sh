#!/usr/bin/expect -f

# Canvia les credencials per les teves propies !!
set username "astrid"
set email "dominguezcastellanoastrid@gmail.com"
set password "1234"

puts "Iniciant migracions de Django..."

# 1. Elimina la base de dades i les migracions
exec rm -rf db.sqlite3 processdata/migrations 

# 2. Fa les migracions necessaries en silenci redirigint la sortida estandard i error a /dev/null 
exec bash -c {python3 manage.py makemigrations processdata > /dev/null 2>&1}
exec bash -c {python3 manage.py migrate > /dev/null 2>&1}

# espera de 10s entre cada interacció
set timeout 10

# 3. Creació de super usuari (per la zona admin)
spawn bash -c {env PYTHONASYNCIODEBUG=0 python3 manage.py createsuperuser > /dev/null 2>&1}

# 4. Omple les credencials automàticament
expect -re ".*Nombre de usuario.*:"
send "$username\r"

expect "Dirección de correo electrónico:"
send "$email\r"

expect "Password:"
send "$password\r"

expect "Password (again):"
send "$password\r"

expect "Bypass password validation and create user anyway?"
send "y\r"

# espera fins que finalitza el procés
expect eof
