# Bidragsguide

Heisann sveisann! Er du interessert i å bidra? Kult!

Det er derimot noen kodestilsregler jeg ønsker at skal følges. Dette dokumentet fungerer som en defacto regelbok for både meg og/eller andre.

## Sjekk koden din

Viktigst av alt er at koden din består flake8 sin PEP8-test. Dette kan du teste på egen maskin ved å installere flake8:

```
pip install flake8
```

for å så kjøre følgende kommando:

```
flake8 --max-line-length=120 --show-source
```

## Regler

### Typing

All kode skal være typet til beste evne. Dette betyr at man for eksempel også gjerne bør spesifisere typene innad i en dict eller lignende.

### Docstrings

Alle funksjoner skal ha docsstrings som følger denne stilen:

```python
def greet(self, navn: str) -> str:
    """
    Greets the invoking user using the inputted name

    Parameters
    ----------
    navn (str): The user's inputted name

    Returns
    ----------
    (str): A greeting
    """

    return f'Hello, {name}'
```

Sløyf alt som ikke brukes.

### Sortering av imports

Alle imports skal være gruppert på følgende måte:

1. Standardbibliotek
2. Tredjepartsbibliotek
3. Lokal kode

Innad i hver gruppe skal importeringer sortert alfabetisk med vekt på forelderpakken. Det vil si at hvis du importerer bare en del av en pakke skal den fortsatt være sortert i henhold til forelderpakkens navn.

### Rekkefølge på kommandosjekker (decorators)

Hver kommando er en funksjon som har et eller flere decorators over seg. Dette er sjekker som utføres før kommandoen kjøres. En av disse konverterer også funksjonen til en faktisk kommando som vi kan kjøre gjennom Discord.

Decorators skal sorteres som følgende:

1. is owner
2. Guild only
3. Bot permissions
4. User permissions
5. Cooldown
6. Kommando (denne må alltid være med)

Merk deg at ikke alle disse trenger å være med, og ikke alle sjekker som finnes er nevnt her. Bruk hodet og tenk hva som er logisk for deg om du møter på en slik situasjon.

### Quotation marks

Ta i bruk enkle quotation marks `'` der det er mulig. Multiline comments skal skrives med dobble quotation marks `"`.

### Newline mellom docstring og kode samt mellom siste kodelinje returstatement

Ja, det tittelen sier. Det er et unntak for returstatements hvis det er tatt i bruk early returning.

### Norske parameternavn i kommandoer

Selv om Discord.py 2.0 støtter oversettelser, er ikke dette noe vi implementerer. Med tanke på at botten er norsk og for norske brukere må dette reflekteres i parameternavn siden dette er hva Discord bruker som grensesnitt for kommandoer.

### Engelsk for alt annet

All annen kode holdes på engelsk. Dette inkluderer kommentarer.

Et tips er å ha et engelsk funksjonsnavn, men spesifisere i decoratoren over med navnparameteren.

### Avhengigheter

Hvis en ny avhengighet trengs, sørg for å spesifisere major og minor versjon i requirementsfila.


## Ønsket utforming av ny funksjonalitet

- Bruk embeds til feilmeldinger og som respons om mulig.
- Sett cooldown til 5 sekunder for kommandoer som krever eksterne API kall eller særlig mye prosessering.
    - Ellers, settes denne til 2 sekunder.
