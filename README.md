# cakebar

CakeBar — shirinliklar onlayn-do'koni (Django). Mahsulotlar, savat, buyurtma, pulni qaytarish (refund), wallet, sevimlilar, sharhlar, promo-kodlar, bildirishnomalar, admin panel va UZ/RU/EN til qo'llab-quvvatlash.

## Lokal ishga tushirish

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py seed_pages
python manage.py createsuperuser
python manage.py runserver
```

## Internetga chiqarish (Railway / Render)

Loyiha deploy uchun tayyor (`Procfile`, `requirements.txt`, `runtime.txt`, Whitenoise static fayllar uchun sozlangan). Qilish kerak bo'lgan yagona narsa — quyidagi muhit o'zgaruvchilarini (environment variables) hosting panelida sozlash:

| O'zgaruvchi | Tavsif |
|---|---|
| `CAKEBAR_SECRET_KEY` | tasodifiy uzun maxfiy satr (masalan `python -c "import secrets;print(secrets.token_urlsafe(50))"`) |
| `CAKEBAR_DEBUG` | `False` (production uchun) |
| `CAKEBAR_ALLOWED_HOSTS` | domeningiz, masalan `cakebar.up.railway.app` |
| `CAKEBAR_CSRF_TRUSTED_ORIGINS` | `https://cakebar.up.railway.app` |
| `CAKEBAR_DATABASE_URL` | (ixtiyoriy) PostgreSQL uchun, bo'lmasa SQLite ishlatiladi |

Ixtiyoriy — real email/SMS uchun: `CAKEBAR_EMAIL_HOST`, `CAKEBAR_EMAIL_HOST_USER`, `CAKEBAR_EMAIL_HOST_PASSWORD`, `ESKIZ_EMAIL`, `ESKIZ_PASSWORD`.

Bular sozlanmasa ham sayt to'liq ishlaydi — faqat SMS/email jo'natilmaydi (saytdagi bildirishnoma tizimi baribir ishlaydi).
