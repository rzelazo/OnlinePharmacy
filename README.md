# OnlinePharmacy

## Postawiona, działająca strona z aplikacją dostępna jest pod adresem:
https://blachotrapez.pythonanywhere.com/

### Strona logowania:
![image](https://user-images.githubusercontent.com/62251572/175108427-ebaf8cbb-f4cc-477a-b8fd-f6cc1aa32d2a.png)

Żeby sie zalogować jako admin:  
##### Username:  
```
admin
```
##### Password: 
```
haslo1234
```

Żeby się zalogować jako user:
##### Username:  
```
grzegorz
```
##### Password: 
```
haslo1234
```

## Jeśli chcemy uruchomić serwer samodzielnie: 
### Wymagane technologie
- [Python 3.9](https://www.python.org/downloads/release/python-390/)
- [Django 3.2.5](https://pypi.org/project/Django/3.2.5/)
- [SQLite3](https://www.sqlite.org/index.html)
- [django-allauth 0.50.0](https://django-allauth.readthedocs.io/en/latest/installation.html)
- [python-decouple 3.6](https://pypi.org/project/python-decouple/3.6)

Generalnie wystarczy sam [Python](https://www.python.org/) i [pip](https://pypi.org/project/pip/), reszta zależności dociągnięta może zostać za pomocą [pip-a](https://pypi.org/project/pip/) przy wykorzystaniu pliku `requirements.txt`
```
pip install -r requirements.txt
```

### Jak uruchomić:
- klonujemy repozytorium
- wchodzimy do folderu root projektu: OnlinePharmacy (konsole odpalamy w folderze, w którym są podfoldery: core, media, OnlinePharmacy, static oraz pliki manage.py i requirements.txt)

![image](https://user-images.githubusercontent.com/62251572/170886277-42ad4996-c7b1-4d9f-b3ad-9597c2511730.png)

- zeby pobrać dependencies odpalamy konsole i wpisujemy:
```
pip install -r requirements.txt
```
- kiedy wszystko się pobierze i zainstaluje to znowu w konsoli wpisujemy:
```
python manage.py check
```  
- Jeśli nie wyskoczy błąd i wyświetli się, że jest no issues:

![image](https://user-images.githubusercontent.com/62251572/170886440-b6ab56bb-87d2-4fc6-892f-769be7066947.png)

To wszystko jest w porządku i można odpalić serwer - w konsolce trzeba wpisać:
```
python manage.py runserver
```
![image](https://user-images.githubusercontent.com/62251572/170886535-a6527acd-bfe9-4699-a359-85449b2d3b5f.png)

- Żeby wejść na strone w wyszukiwarke wpisujemy adres serwera, który wyświetlił się w konsoli
```
http://127.0.0.1:8000/
```

## Żeby wyświetlała się nasza strona błędu zamiast domyślnej strony błędu debuga należy wyłączyć tryb debug:
1. W OnlinePharmacy/settings.py trzeba zmienić wartość zmiennej DEBUG:
```
DEBUG = False
```
2. Serwer trzeba odpalać inną komendą
```
python manage.py runserver --insecure
```
