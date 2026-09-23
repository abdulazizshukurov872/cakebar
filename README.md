# cakebar

CakeBar — shirinliklar onlayn-do'koni (Django). Mahsulotlar, savat, buyurtma, pulni qaytarish (refund), wallet, sevimlilar, sharhlar, promo-kodlar, bildirishnomalar, admin panel va UZ/RU/EN til qo'llab-quvvatlash.

Qo'shimcha: yetkazish kuni va vaqt oralig'ini tanlash, tort ustiga yozuv va og'irlik (kg) tanlash, yetkazish narxi va minimal buyurtma, kuryer paneli (`/courier/`), admin Telegram guruhiga yangi buyurtma xabari, Telegram Mini App.

## Lokal ishga tushirish

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py seed_pages
python manage.py createsuperuser
python manage.py runserver
```

Testlar: `python manage.py test`

To'lanmagan karta buyurtmalarini bekor qilish (zaxirani bo'shatish): `python manage.py expire_unpaid_orders` (doimiy ishlashi uchun `--loop`).

## Internetga chiqarish (Railway / Render)

Loyiha deploy uchun tayyor (`Procfile`, `requirements.txt`, `runtime.txt`, Whitenoise). Railway/Render'da `CAKEBAR_DEBUG` sukut bo'yicha `False` bo'ladi, `CAKEBAR_SECRET_KEY` va ma'lumotlar bazasi berilmasa sayt ishga tushmaydi — bu ataylab, ma'lumot yo'qolmasligi uchun.

`Procfile` da uchta jarayon bor: `web` (sayt), `release` (migratsiya), `worker` (to'lanmagan buyurtmalarni har 5 daqiqada bekor qiladi). Railway'da `worker` ni alohida servis qilib qo'shing.

### Majburiy

| O'zgaruvchi | Tavsif |
|---|---|
| `CAKEBAR_SECRET_KEY` | tasodifiy uzun maxfiy satr (`python -c "import secrets;print(secrets.token_urlsafe(50))"`) |
| `CAKEBAR_ALLOWED_HOSTS` | domeningiz, masalan `cakebar.up.railway.app` |
| `CAKEBAR_CSRF_TRUSTED_ORIGINS` | `https://cakebar.up.railway.app` |
| `CAKEBAR_DATABASE_URL` | PostgreSQL manzili (Railway'da Postgres qo'shsangiz `DATABASE_URL` avtomatik o'qiladi) |
| `CAKEBAR_MEDIA_ROOT` | yuklangan rasmlar uchun doimiy disk (volume) yo'li, masalan `/data/media` |

### Ixtiyoriy

| O'zgaruvchi | Sukut | Tavsif |
|---|---|---|
| `CAKEBAR_DELIVERY_FEE` | 15000 | yetkazish narxi (so'm) |
| `CAKEBAR_FREE_DELIVERY_FROM` | 200000 | shu summadan yetkazish bepul (0 = hech qachon) |
| `CAKEBAR_MIN_ORDER_AMOUNT` | 30000 | minimal buyurtma summasi |
| `CAKEBAR_INSCRIPTION_FEE` | 0 | tortga yozuv narxi |
| `CAKEBAR_DELIVERY_LEAD_HOURS` | 2 | vaqt oralig'i boshlanishidan kamida necha soat oldin buyurtma berish kerak |
| `CAKEBAR_UNPAID_ORDER_TTL_MINUTES` | 30 | karta orqali to'lanmagan buyurtma necha daqiqadan keyin bekor bo'ladi |
| `CAKEBAR_LOGIN_RATE_LIMIT` | 5 | 15 daqiqada nechta noto'g'ri kirish urinishiga ruxsat |
| `CAKEBAR_TELEGRAM_BOT_TOKEN` | — | Telegram bot tokeni |
| `CAKEBAR_TELEGRAM_ADMIN_CHAT_ID` | — | yangi buyurtma/refund xabarlari boradigan guruh ID si |
| `CAKEBAR_SITE_URL` | — | saytning `https://` manzili (Mini App uchun) |
| `ESKIZ_EMAIL`, `ESKIZ_PASSWORD` | — | SMS (Eskiz). Sozlansa, ro'yxatdan o'tishda SMS kod so'raladi |
| `CAKEBAR_EMAIL_HOST`, `CAKEBAR_EMAIL_HOST_USER`, `CAKEBAR_EMAIL_HOST_PASSWORD` | — | email |
| `CAKEBAR_PAYME_MERCHANT_ID`, `CAKEBAR_PAYME_KEY` | — | Payme |
| `CAKEBAR_CLICK_MERCHANT_ID`, `CAKEBAR_CLICK_SERVICE_ID`, `CAKEBAR_CLICK_SECRET_KEY` | — | Click |

Telegram botni production'ga ulash (webhook + "Do'kon" Mini App tugmasi): `python manage.py telegram_set_webhook`. Lokalda esa `python manage.py telegram_poll`.

## Kuryerlar

Admin panel → **Kuryerlar** bo'limida kuryer qo'shing va unga saytdagi hisobini biriktiring. Buyurtma "Tasdiqlangan" bo'lganda eng kam band kuryerga avtomatik biriktiriladi. Kuryer saytga kirib `/courier/` sahifasida o'z buyurtmalarini ko'radi va "Yo'lga chiqdim" / "Yetkazildi" tugmalarini bosadi.

## Tort parametrlari

Admin → Mahsulot: **"Og'irlik bo'yicha sotiladi"** belgilansa, narx 1 kg uchun hisoblanadi va mijoz 1–3 kg tanlaydi. **"Yozuv yozish mumkin"** belgilansa, mijoz tort ustiga yoziladigan matnni kiritadi ("Tortlar" kategoriyasida sukut bo'yicha yoqilgan).
