# UiO Gaming Discord Bot

UiO Gaming Discord Bot er en chattebot for ulike formål. Hvilke formål det er, er jeg ikke helt sikker på.

## Installasjon

1. Fjern `.example` fra [config.yaml.example](src/config/config.yaml) i configmappen

2. Fyll inn verdiene i denne configfilen

Du kan så bevege deg videre til ett av to alternativer.

### Valgmulighet 1 - Manuelt

Du bør ha gjort følgende:

- Installert Python 3.12+
- Ha en Postgresql database satt opp


1. Installer avhengigheter

```
pip install -r requirements.txt -U
```

2. Kjør bot

```
python src/run.py
```

### Valgmulighet 2 - Docker

```
docker-compose up
```

## Bidra

Se [CONTRIBUTING.md](CONTRIBUTING.md)
