from django.core.management.base import BaseCommand

from pages.models import JobOpening, Location

LOCATIONS = [
    ("CakeBar Chilonzor", "Bunyodkor ko'chasi 12, Chilonzor tumani", "+998 71 200 00 01", "09:00 – 22:00"),
    ("CakeBar Yunusobod", "Amir Temur shoh ko'chasi 45, Yunusobod tumani", "+998 71 200 00 02", "09:00 – 22:00"),
    ("CakeBar Mirzo Ulug'bek", "Buyuk Ipak Yo'li ko'chasi 7, Mirzo Ulug'bek tumani", "+998 71 200 00 03", "08:00 – 23:00"),
    ("CakeBar Yakkasaroy", "Shota Rustaveli ko'chasi 21, Yakkasaroy tumani", "+998 71 200 00 04", "09:00 – 22:00"),
    ("CakeBar Sergeli", "Qatortol ko'chasi 3, Sergeli tumani", "+998 71 200 00 05", "09:00 – 21:00"),
    ("CakeBar Samarqand", "Registon ko'chasi 8, Samarqand shahri", "+998 66 200 00 06", "09:00 – 22:00"),
]

JOBS = [
    ("Qandolatchi", "Ishlab chiqarish", "Toshkent", "Tort va pirojnoye tayyorlash bo'yicha tajribali qandolatchi talab qilinadi."),
    ("Baker (novvoy)", "Ishlab chiqarish", "Toshkent", "Non va xamir mahsulotlari ustasi."),
    ("Kuryer", "Yetkazib berish", "Toshkent", "Shaxsiy avtomobil yoki mototsikl bo'lishi kerak."),
    ("Sotuv menejeri", "Savdo", "Toshkent", "Filialda mijozlarga xizmat ko'rsatish."),
    ("SMM mutaxassisi", "Marketing", "Toshkent (masofaviy)", "Instagram va Telegram kontent boshqaruvi."),
]


class Command(BaseCommand):
    help = "Filiallar va vakansiyalarni yaratadi"

    def handle(self, *args, **options):
        Location.objects.all().delete()
        JobOpening.objects.all().delete()

        for i, (name, address, phone, hours) in enumerate(LOCATIONS):
            Location.objects.create(name=name, address=address, phone=phone, working_hours=hours, order=i)

        for title, dept, loc, desc in JOBS:
            JobOpening.objects.create(title=title, department=dept, location=loc, description=desc, is_active=True)

        self.stdout.write(self.style.SUCCESS(f"{len(LOCATIONS)} filial va {len(JOBS)} vakansiya yaratildi."))
