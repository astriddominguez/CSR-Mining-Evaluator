# Mining-CSR-Evaluator


Aplicació web per calcular l’índex de Responsabilitat Social Corporativa (CSR) d’un projecte miner.  
L’eina permet a l’usuari completar un formulari interactiu i obté una puntuació basada en les dimensions **ambiental** i **socioeconòmica**, segons l’article [Corporate Social Responsibility Index for Mine Sites (Bascompta et al., 2022)](https://doi.org/10.3390/su142013570).

## Requisits

- Python 3.10
- Django 5.2.2
- Pip3 (gestor de paquets)
- Entorn virtual recomanat

## Crear entorn virtual

És recomanable utilitzar un entorn virtual per aïllar les dependències del projecte.

### Linux / MacOS:
```bash
python3 -m venv env
source env/bin/activate
```

## Instal·lar depèndencies 
```bash
pip3 install -r requirements.txt
```

## Executar localment 

Si és la **primera vegada** que clones el projecte o vols començar des de zero (amb la base de dades neta), pots utilitzar l’script `update_models.sh` per preparar l'entorn automàticament. En cas contrari, pots passar directament a la secció **Execució final**.

### 🔁 Script: `update_models.sh`

Aquest script fa el següent:

1. Elimina la base de dades (`db.sqlite3`) i les migracions de l’app `processdata`.
2. Torna a generar les migracions.
3. Aplica les migracions per crear la base de dades.
4. Crea un superusuari automàticament amb:
   - Usuari: `John`
   - Correu: `Jonh@gmail.com`
   - Contrasenya: `1234`

> 🔐 **Important:** Aquestes credencials són d'exemple.  
> Si utilitzes aquest script, **recorda editar el fitxer `update_models.sh`** i substituir les dades pel teu nom d'usuari, correu i contrasenya preferits, tenint en compte que aquesta última sigui segura. 

### Per executar-lo:

```bash
chmod +x update_models.sh
./update_models.sh
```

## Accions prèvies a l'execució:
Per preparar l’aplicació per a producció, és necessari col·leccionar els fitxers estàtics amb:

```bash
python3 manage.py collectstatic
```

> **Nota**: En local, no cal executar collectstatic si Django està en mode DEBUG = True.

## Execució final

```bash
python3 manage.py runserver
```

## Executar els tests

Per executar els tests automatitzats del projecte:

```bash
python3 manage.py test
```

## Estructura del projecte

```text
CSR-Mining-Evaluator/
├── core/ # Configuració general del projecte Django
│ ├── settings.py # Fitxer principal de configuració (BD, apps, rutes, etc.)
│ ├── urls.py # Rutes globals del projecte
│ ├── wsgi.py # Punt d’entrada WSGI per desplegament (ex. PythonAnywhere)
│ └── asgi.py # Punt d’entrada ASGI per funcionalitats asíncrones (WebSockets, etc.)
│
├── processdata/              # App principal amb la lògica del formulari i càlculs CSR
│   ├── views.py              # Vistes per gestionar el formulari, resultats i rutes internes
│   ├── urls.py               # Rutes específiques d’aquesta app
│   ├── models.py             # Models de la base de dades (formularis, subformularis, etc.)
│   ├── tests.py              # Tests per validar el comportament del sistema
│   ├── data.py               # Càrrega de metadades dels fitxers JSON de la carpeta /config
│   ├── getdata.py            # Funcions per llegir/escriure dades a la base de dades
│   ├── clean_bd.py           # Script per netejar registres antics de la base de dades
│   ├── admin.py              # Configuració de l’àrea d’administració 
│   ├── apps.py               # Configuració de l’app dins del projecte Django
│   ├── utils.py              # Funcions auxiliars reutilitzables
│   ├── migrations/           # Migracions generades per Django
│   ├── config/               # Fitxers JSON amb metadades de preguntes i estructures de formularis
│   └── rating/               # Mòduls encarregats de calcular les puntuacions CSR
|
│
├── env/ # Entorn virtual Python 
│
├── templates/ # Plantilles HTML de l’aplicació
│ └── pages/ # Plantilles específiques (evaluator.html, results.html, tutorial.html)
│
├── staticfiles/ # Arxius estàtics: CSS, JS, imatges, icones
│
├── db.sqlite3 # Base de dades SQLite local (es genera automàticament)
├── .env # Fitxer de variables d’entorn (SECRET_KEY, DEBUG, etc.)
├── LICENSE # Llicència del projecte (MIT)
├── manage.py # Script principal per gestionar el projecte Django
├── requirements.txt # Llista de paquets Python necessaris per executar el projecte
├── update_models.sh # Script per reiniciar la BD i crear un superusuari automàticament
└── README.md 
```
