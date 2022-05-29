# OnlinePharmacy

## Jak odpalić:
- trzeba mieć zainstalowany Pytong
- pobieramy repo
- wchodzimy do folderu root projektu: OnlinePharmacy (konsole odpalamy w folderze, w którym są podfoldery: core, media, OnlinePharmacy, static oraz pliki manage.py i requirements.txt)

![image](https://user-images.githubusercontent.com/62251572/170886277-42ad4996-c7b1-4d9f-b3ad-9597c2511730.png)

- zeby pobrać dependencies odpalamy konsolke i wklepujemy:
```
pip install -r requirements.txt
```
- jak wszystko sie pobierze i zainstaluje to znowu w konsolce wklepujemy:
```
python manage.py check
```  
- Jeśli nie wywali błędu i wyświetli, że jest no issues:

![image](https://user-images.githubusercontent.com/62251572/170886440-b6ab56bb-87d2-4fc6-892f-769be7066947.png)

To wszystko jest gitara i można odpalić serwer - w konsolce trzeba wpisać:
```
python manage.py runserver
```
![image](https://user-images.githubusercontent.com/62251572/170886535-a6527acd-bfe9-4699-a359-85449b2d3b5f.png)

- Żeby wejść na strone w wyszukiwarke wpisujemy adres serwera co sie wyświetlił w konsolce
```
http://127.0.0.1:8000/
```

![image](https://user-images.githubusercontent.com/62251572/170886773-0df006c7-dee2-49bd-9108-d7f47274a63b.png)

Żeby sie zalogować jako admin to:
Username: `admin`
Password: `dupa1234`

I jesteśmy na stronce.

Stronki HTML są w folderze `templates`:
 - Te dotyczące samej apteki są w folderze: `templates/core`
 - Te od logowania, rejestrowania, wylogowania itp są w folderze: `templates/account`

CSS, Javascript i obrazki dodaje sie do folderu `static`.

https://docs.djangoproject.com/en/3.2/ref/templates/language/
