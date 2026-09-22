from django.core.management.base import BaseCommand

from catalog.models import Category, Product

IMG = "https://images.unsplash.com/photo-{}?w=800&q=80&auto=format&fit=crop"

A = IMG.format("1578985545062-69928b1d9587")   # chocolate cake
B = IMG.format("1587248720327-8eb72564be1e")   # berry cake
C = IMG.format("1519340241574-2cec6aef0c01")   # wedding cake
D = IMG.format("1587668178277-295251f900ce")   # cupcakes
E = IMG.format("1551024506-0bccd828d307")      # donuts
F = IMG.format("1533910534207-90f31029a78e")   # donut
G = IMG.format("1499636136210-6f4ee915583e")   # cookies
H = IMG.format("1569864358642-9d1684040f43")   # macarons
I_ = IMG.format("1582058091505-f87a2e55a40f")  # gummy candy
J = IMG.format("1511381939415-e44015466834")   # chocolate bars
K = IMG.format("1497034825429-c343d7c6a68f")   # ice cream cone
L = IMG.format("1560008581-09826d1de69e")      # ice cream bowl
M = IMG.format("1587132137056-bfbf0166836e")   # dessert table
N = IMG.format("1461023058943-07fcbe16d735")   # cake
O = IMG.format("1546069901-ba9599a7e63c")      # cake slice
P = IMG.format("1541783245831-57d6fb0926d3")   # cake
Q = IMG.format("1571877227200-a0d98ea607e9")   # pink donuts
S = IMG.format("1621939514649-280e2ee25f60")   # chocolate candy
T = IMG.format("1606313564200-e75d5e30476c")   # national sweet
U = IMG.format("1571506165871-ee72a35bc9d4")   # national sweet
V = IMG.format("1610450949065-1f2841536c88")   # chocolate chunks
W = IMG.format("1478144592103-25e218a04891")   # cupcake
Y = IMG.format("1571115177098-24ec42ed204d")   # national sweet
AA = IMG.format("1606983340126-99ab4feaa64a")  # candy jar
AB = IMG.format("1621303837174-89787a7d4729")  # lemon cake
DR1 = IMG.format("1600271886742-f049cd451bba")  # juice glass
DR2 = IMG.format("1621506289937-a8e4df240d0b")  # orange juice
DR3 = IMG.format("1613478223719-2ab802602423")  # smoothie
DR7 = IMG.format("1622597467836-f3285f2131b8")  # milkshake
CF1 = IMG.format("1447933601403-0c6688de566e")  # espresso
CF2 = IMG.format("1494314671902-399b18174975")  # cappuccino
CF3 = IMG.format("1521737604893-d14cc237f11d")  # latte
CF4 = IMG.format("1522992319-0365e5f11656")     # americano
CB1 = IMG.format("1587132137056-bfbf0166836e")  # dessert table
CB2 = IMG.format("1495474472287-4d71bcdd2085")  # flatlay combo
CB3 = IMG.format("1517686469429-8bdb88b9f907")  # flatlay combo

CATEGORIES = [
    ("tort", "Tortlar"),
    ("pirojnoye", "Pirojnoye va desertlar"),
    ("donut", "Donutlar"),
    ("pechenye", "Pechenye"),
    ("shokolad", "Shokoladlar"),
    ("konfet", "Konfetlar"),
    ("makaron", "Makaronlar"),
    ("muzqaymoq", "Muzqaymoq"),
    ("milliy", "Milliy shirinliklar"),
    ("keks", "Keks va muffinlar"),
    ("ichimlik", "Ichimliklar"),
    ("qahva", "Qahva"),
    ("combo", "Haftalik chegirmalar"),
]

# (name, desc, category_key, price, discount, in_stock, rating, image_url, composition)
PRODUCTS = [
    ("Shokoladli tort", "Uch qavatli, krem bilan", "tort", 250000, 210000, True, 4.8, A,
     "Bug'doy uni, shakar, tuxum, kakao kukuni, sariyog', sut, ishlov berilgan shokolad, pishirish kukuni"),
    ("Rezavorli tort", "Yovvoyi rezavorlar bilan bezatilgan", "tort", 280000, None, True, 4.7, B,
     "Bug'doy uni, shakar, tuxum, sariyog', qaymoq krem, mavsumiy rezavorlar (qulupnay, malina, ko'k smorodina)"),
    ("Nikoh torti", "Oq krem, ko'p qavatli", "tort", 450000, None, True, 4.9, C,
     "Bug'doy uni, shakar, tuxum, sariyog', vanil ekstrakti, oq shokolad, mastika bezak"),

    ("Napoleon pirojnoye", "Qatlamli xamir, vanil krem", "pirojnoye", 18000, None, True, 4.6, N,
     "Qatlamli xamir (un, sariyog', tuxum), vanil krem (sut, shakar, tuxum sarig'i, kraxmal)"),
    ("Tiramisu", "Kofe va mascarpone bilan", "pirojnoye", 32000, 27000, True, 4.8, O,
     "Mascarpone pishloq, savoyardi pechenye, espresso kofe, kakao kukuni, tuxum, shakar"),
    ("Ezoklair", "Shokolad glazur bilan", "pirojnoye", 16000, None, True, 4.5, P,
     "Zavarnoy xamir (un, sariyog', tuxum), vanil krem, shokolad glazur"),

    ("Klassik donut", "Shakar glazur bilan", "donut", 15000, None, True, 4.4, E,
     "Bug'doy uni, shakar, xamirturush, sut, tuxum, o'simlik moyi, shakar glazur"),
    ("Shokoladli donut", "Shokolad glazur, sprinkle", "donut", 17000, 14000, True, 4.6, F,
     "Bug'doy uni, shakar, xamirturush, sut, tuxum, shokolad glazur, rangli sprinkle"),
    ("Pushti glazurli donut", "Meva ta'mi glazur", "donut", 17000, None, True, 4.5, Q,
     "Bug'doy uni, shakar, xamirturush, sut, tuxum, meva ta'mli glazur (qulupnay)"),

    ("Choco-chip pechenye", "12 dona quti", "pechenye", 32000, None, True, 4.6, G,
     "Bug'doy uni, sariyog', jigarrang shakar, tuxum, shokolad bo'lakchalari, vanil"),
    ("Oatmeal pechenye", "Yormali, asal bilan", "pechenye", 28000, 24000, True, 4.4, G,
     "Suli yormasi, bug'doy uni, asal, sariyog', mayiz, tarkan"),
    ("Assorti pechenye to'plami", "Turli shakldagi pechenyelar", "pechenye", 35000, None, True, 4.5, M,
     "Bug'doy uni, sariyog', shakar, tuxum, vanil — turli shakl va ta'mlar aralashmasi"),

    ("Qora shokolad 70%", "100gr plitka", "shokolad", 30000, None, True, 4.7, J,
     "Kakao massasi (70%), kakao moyi, shakar, kakao kukuni"),
    ("Sut shokoladi yong'oqli", "100gr", "shokolad", 27000, None, True, 4.5, V,
     "Sut kukuni, kakao moyi, shakar, yeryong'oq/findiq, kakao massasi"),
    ("Shokolad konfet to'plami", "Aralash quti, 300gr", "shokolad", 45000, 39000, True, 4.7, S,
     "Sut va qora shokolad, praline, yong'oq, meva to'ldirmalari"),

    ("Jele konfetlar", "Meva ta'mi, 300gr", "konfet", 25000, None, True, 4.3, I_,
     "Shakar, glyukoza siropi, jelatin, meva sharbati kontsentrati, limon kislotasi"),
    ("Karamel konfet", "Yumshoq karamel, 250gr", "konfet", 22000, None, False, 4.2, AA,
     "Shakar, glyukoza siropi, sariyog', qaymoq, vanil"),
    ("Marmelad konfetlar", "Rangli, 250gr", "konfet", 24000, None, True, 4.3, I_,
     "Shakar, pektin, meva sharbati, limon kislotasi, tabiiy bo'yoqlar"),

    ("Rangli makaron to'plami", "12 dona, aralash ta'm", "makaron", 38000, None, True, 4.8, H,
     "Bodom uni, quandagi oqsil, shakar, pishirish kukuni, turli ta'mli kremlar"),
    ("Vanil makaron", "6 dona", "makaron", 22000, None, True, 4.6, H,
     "Bodom uni, tuxum oqsili, shakar, vanil kremi"),
    ("Shokoladli makaron", "6 dona", "makaron", 22000, 19000, True, 4.7, H,
     "Bodom uni, tuxum oqsili, shakar, shokolad ganash"),

    ("Vanil muzqaymoq", "500ml", "muzqaymoq", 28000, None, True, 4.5, K,
     "Sut, qaymoq, shakar, tuxum sarig'i, tabiiy vanil"),
    ("Shokoladli muzqaymoq", "500ml", "muzqaymoq", 28000, None, True, 4.6, L,
     "Sut, qaymoq, shakar, kakao, shokolad bo'lakchalari"),
    ("Rezavorli sorbet", "500ml, sut mahsulotsiz", "muzqaymoq", 30000, None, True, 4.4, K,
     "Meva pyuresi (rezavorlar), shakar, suv, limon sharbati"),

    ("Halva", "An'anaviy, yong'oqli, 400gr", "milliy", 32000, None, True, 4.6, T,
     "Kunjut yog'i, shakar siropi, sovun ildizi ekstrakti, yong'oq"),
    ("Parvarda", "Qand asosida tayyorlangan, 300gr", "milliy", 20000, None, True, 4.4, U,
     "Shakar, suv, limon kislotasi, vanil"),
    ("Chak-chak", "Asal bilan, 400gr", "milliy", 26000, None, True, 4.5, Y,
     "Un, tuxum, asal, o'simlik moyi (qovurish uchun)"),

    ("Vanil keksi", "Mini keks, 6 dona", "keks", 24000, None, True, 4.5, D,
     "Bug'doy uni, sariyog', shakar, tuxum, vanil, pishirish kukuni"),
    ("Shokoladli muffin", "6 dona", "keks", 26000, 22000, True, 4.6, W,
     "Bug'doy uni, kakao, shakar, tuxum, sariyog', shokolad bo'lakchalari"),
    ("Limonli keks", "Limon glazur bilan", "keks", 27000, None, True, 4.5, AB,
     "Bug'doy uni, sariyog', shakar, tuxum, limon qobig'i va sharbati, glazur"),

    ("Apelsin sharbati", "Yangi siqilgan, 500ml", "ichimlik", 18000, None, True, 4.6, DR2,
     "100% apelsin sharbati, konservantsiz"),
    ("Qulupnay smuzi", "Tabiiy, 400ml", "ichimlik", 20000, None, True, 4.5, DR3,
     "Qulupnay, banan, tabiiy yogurt, asal"),
    ("Limonad", "Uy usulida, 500ml", "ichimlik", 15000, None, True, 4.4, DR1,
     "Suv, limon sharbati, shakar, yalpiz"),
    ("Shokoladli milkshake", "450ml", "ichimlik", 22000, 18000, True, 4.7, DR7,
     "Sut, muzqaymoq, shokolad siropi, qaymoq"),

    ("Espresso", "30ml, klassik", "qahva", 12000, None, True, 4.6, CF1,
     "100% arabika kofe donlari"),
    ("Kapuchino", "200ml, sut ko'pigi bilan", "qahva", 18000, None, True, 4.7, CF2,
     "Espresso, bug'langan sut, sut ko'pigi"),
    ("Latte", "250ml, yumshoq ta'm", "qahva", 20000, None, True, 4.6, CF3,
     "Espresso, ko'p sut, ozgina sut ko'pigi"),
    ("Amerikano", "220ml", "qahva", 14000, None, True, 4.4, CF4,
     "Espresso, issiq suv"),

    ("Napoleon + Espresso", "Kombinatsiya: 1 ta Napoleon pirojnoye + 1 ta espresso", "combo", 30000, 16500, True, 4.8, CB1,
     "Napoleon pirojnoye (qatlamli xamir, vanil krem) + espresso (arabika)"),
    ("Tiramisu + Kapuchino", "Kombinatsiya: 1 ta tiramisu + 1 ta kapuchino", "combo", 50000, 27500, True, 4.9, CB2,
     "Tiramisu (mascarpone, kofe, kakao) + kapuchino (espresso, sut ko'pigi)"),
    ("Shokoladli tort + Latte", "Kombinatsiya: tort bo'lagi + 1 ta latte", "combo", 45000, 24500, True, 4.7, CB3,
     "Shokoladli tort bo'lagi + latte (espresso, sut)"),
    ("2 ta Donut + Amerikano", "Kombinatsiya: 2 ta donut + 1 ta amerikano", "combo", 40000, 22000, True, 4.6, E,
     "Klassik va shokoladli donut + amerikano"),
    ("Makaron seti + Espresso", "Kombinatsiya: 6 dona makaron + 1 ta espresso", "combo", 48000, 26000, True, 4.8, H,
     "Aralash ta'mli makaronlar + espresso"),
    ("Ezoklair + Kapuchino", "Kombinatsiya: 1 ta ezoklair + 1 ta kapuchino", "combo", 34000, 18500, True, 4.6, P,
     "Ezoklair (zavarnoy xamir, vanil krem) + kapuchino"),
    ("Shokoladli muffin + Limonad", "Kombinatsiya: 1 ta muffin + 1 ta limonad", "combo", 38000, 21000, True, 4.5, W,
     "Shokoladli muffin + uy usulida limonad"),
    ("Chak-chak + Qora kofe", "Kombinatsiya: chak-chak porsiyasi + 1 ta amerikano", "combo", 42000, 23000, True, 4.6, Y,
     "Chak-chak (un, asal) + amerikano"),
    ("Pechenye to'plami + Milkshake", "Kombinatsiya: pechenye seti + 1 ta milkshake", "combo", 46000, 25000, True, 4.7, G,
     "Assorti pechenye + shokoladli milkshake"),
    ("Rezavorli tort + Smuzi", "Kombinatsiya: tort bo'lagi + 1 ta qulupnay smuzi", "combo", 52000, 28500, True, 4.8, B,
     "Rezavorli tort bo'lagi + qulupnay smuzi"),
]


class Command(BaseCommand):
    help = "CakeBar uchun real rasmli kategoriya va mahsulotlarni yaratadi (mavjudlarini almashtiradi)"

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        cats = {}
        for key, name in CATEGORIES:
            cats[key] = Category.objects.create(name=name)

        for name, desc, cat_key, price, discount, in_stock, rating, image_url, composition in PRODUCTS:
            Product.objects.create(
                name=name, description=desc, category=cats[cat_key],
                price=price, discount_price=discount, in_stock=in_stock,
                rating=rating, image_url=image_url, composition=composition,
            )

        self.stdout.write(self.style.SUCCESS(f"{len(cats)} kategoriya va {len(PRODUCTS)} mahsulot yaratildi."))
