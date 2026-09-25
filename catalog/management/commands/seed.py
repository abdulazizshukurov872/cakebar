from django.core.management.base import BaseCommand

from catalog.models import Category, Product

IMG = "https://images.unsplash.com/photo-{}?w=800&q=80&auto=format&fit=crop"

# Every ID below was downloaded and visually inspected (not just checked for
# HTTP 200) before being assigned to a product — see conversation for the
# verification pass. Only confirmed-correct food photos are used.
A = IMG.format("1578985545062-69928b1d9587")    # rich chocolate drip cake
D = IMG.format("1587668178277-295251f900ce")    # mint chocolate cupcake
E = IMG.format("1551024506-0bccd828d307")       # fudgy brownie w/ ice cream
F = IMG.format("1533910534207-90f31029a78e")    # pink sprinkle donuts
G = IMG.format("1499636136210-6f4ee915583e")    # chocolate chip cookies
H = IMG.format("1569864358642-9d1684040f43")    # macarons stack
I_ = IMG.format("1582058091505-f87a2e55a40f")   # gummy candy
J = IMG.format("1511381939415-e44015466834")    # dark chocolate chunks
K = IMG.format("1497034825429-c343d7c6a68f")    # ice cream cone
L = IMG.format("1560008581-09826d1de69e")       # ice cream bowl w/ sprinkles
N = IMG.format("1461023058943-07fcbe16d735")    # iced coffee glass
P = IMG.format("1541783245831-57d6fb0926d3")    # chocolate bundt cake
Q = IMG.format("1571877227200-a0d98ea607e9")    # tiramisu slice
S = IMG.format("1621939514649-280e2ee25f60")    # boxed chocolate candy bars
T = IMG.format("1606313564200-e75d5e30476c")    # chocolate brownie stack
U = IMG.format("1571506165871-ee72a35bc9d4")    # macarons (alt angle)
V = IMG.format("1610450949065-1f2841536c88")    # chocolate bar + cocoa beans
Y = IMG.format("1571115177098-24ec42ed204d")    # layered tiramisu-style cake
AA = IMG.format("1606983340126-99ab4feaa64a")   # decorated celebration cake
AB = IMG.format("1621303837174-89787a7d4729")   # pink drip birthday cake
DR1 = IMG.format("1600271886742-f049cd451bba")  # orange juice glass
DR2 = IMG.format("1621506289937-a8e4df240d0b")  # orange juice bottle
DR7 = IMG.format("1622597467836-f3285f2131b8")  # smoothies in mason jars
CF1 = IMG.format("1447933601403-0c6688de566e")  # coffee beans
CF2 = IMG.format("1494314671902-399b18174975")  # black coffee cup
CF3 = IMG.format("1521737604893-d14cc237f11d")  # coffee pouring into cup
CF4 = IMG.format("1522992319-0365e5f11656")     # latte-art coffees, toast
FF1 = IMG.format("1568901346375-23c9450c58cd")  # classic cheeseburger
FF2 = IMG.format("1550317138-10000687a72b")     # loaded double burger
FF3 = IMG.format("1565299624946-b28f40a0ae38")  # bbq chicken pizza
FF4 = IMG.format("1513104890138-7c749659a591")  # margherita pizza (close-up)
FF5 = IMG.format("1601924582970-9238bcb495d9")  # pepperoni pizza slice
FF6 = IMG.format("1541592106381-b31e9677c0e5")  # french fries
FF7 = IMG.format("1562967914-608f82629710")     # crispy chicken strips
FF8 = IMG.format("1608039755401-742074f0548d")  # buffalo chicken wings
FF9 = IMG.format("1521305916504-4a1121188589")  # club sandwich
FF10 = IMG.format("1554433607-66b5efe9d304")    # roast beef sandwich
FF11 = IMG.format("1552332386-f8dd00dc2f85")    # street tacos
FF12 = IMG.format("1626700051175-6818013e1d4f") # chicken shawarma wrap
CB3 = IMG.format("1517686469429-8bdb88b9f907")  # boxed chocolate pralines
NI1 = IMG.format("1509365465985-25d11c17e812")  # cinnamon rolls
NI3 = IMG.format("1533134242443-d4fd215305ad")  # cheesecake slice
NI4 = IMG.format("1568051243851-f9b136146e97")  # waffles with raspberries
NI15 = IMG.format("1522336284037-91f7da073525") # macarons close-up
NI16 = IMG.format("1481391319762-47dff72954d9") # mini fruit tarts
NI17 = IMG.format("1495147466023-ac5c588e2e94") # bakery case: croissants/pastry
NI18 = IMG.format("1483695028939-5bb13f8648b0") # single pink glazed donut
NI19 = IMG.format("1626094309830-abbb0c99da4a") # pastel frosted cupcakes

# uz nomi -> (kaloriya kkal/100gr, oqsil g, yog' g, uglevod g) — taxminiy, 100gr/100ml uchun
NUTRITION = {
    "Shokoladli tort": (380, 5.0, 18.0, 50.0),
    "Rezavorli tort": (320, 4.5, 14.0, 45.0),
    "Nikoh torti": (400, 5.5, 20.0, 52.0),
    "Cheesecake": (350, 6.0, 24.0, 28.0),
    "Mevali tart": (280, 4.0, 14.0, 34.0),

    "Napoleon pirojnoye": (420, 5.0, 26.0, 42.0),
    "Tiramisu": (320, 6.0, 20.0, 28.0),
    "Ezoklair": (350, 5.5, 22.0, 33.0),
    "Dolchinli rulet": (380, 6.0, 15.0, 55.0),
    "Kruassan": (410, 8.0, 21.0, 45.0),
    "Belgiya vaflisi": (310, 6.5, 12.0, 42.0),
    "Cannoli": (340, 7.0, 18.0, 36.0),

    "Klassik donut": (360, 5.0, 18.0, 45.0),
    "Shokoladli donut": (390, 5.5, 20.0, 48.0),
    "Pushti glazurli donut": (370, 5.0, 18.0, 47.0),

    "Choco-chip pechenye": (480, 5.5, 24.0, 62.0),
    "Oatmeal pechenye": (430, 6.0, 18.0, 60.0),
    "Assorti pechenye to'plami": (460, 5.5, 22.0, 61.0),

    "Qora shokolad 70%": (550, 7.8, 38.0, 45.0),
    "Sut shokoladi yong'oqli": (540, 8.0, 34.0, 52.0),
    "Shokolad konfet to'plami": (500, 6.5, 30.0, 55.0),
    "Shokoladli brauni": (460, 6.0, 26.0, 52.0),
    "Praline to'plami": (560, 7.0, 36.0, 50.0),

    "Jele konfetlar": (340, 2.0, 0.2, 82.0),
    "Karamel konfet": (400, 1.5, 8.0, 78.0),
    "Marmelad konfetlar": (330, 0.5, 0.1, 84.0),

    "Rangli makaron to'plami": (400, 7.5, 19.0, 54.0),
    "Vanil makaron": (395, 7.0, 18.0, 55.0),
    "Shokoladli makaron": (410, 7.5, 20.0, 53.0),

    "Vanil muzqaymoq": (210, 3.5, 11.0, 24.0),
    "Shokoladli muzqaymoq": (230, 4.0, 12.0, 27.0),
    "Rezavorli sorbet": (130, 0.5, 0.2, 32.0),

    "Halva": (520, 12.0, 30.0, 50.0),
    "Parvarda": (380, 0.2, 0.1, 95.0),
    "Chak-chak": (440, 7.0, 18.0, 62.0),
    "Baklava": (480, 6.5, 28.0, 50.0),

    "Vanil keksi": (390, 5.5, 18.0, 52.0),
    "Shokoladli muffin": (410, 6.0, 20.0, 53.0),
    "Limonli keks": (380, 5.0, 17.0, 54.0),
    "Red Velvet keks": (400, 5.5, 19.0, 53.0),

    "Apelsin sharbati": (45, 0.7, 0.2, 10.0),
    "Qulupnay smuzi": (65, 1.5, 1.0, 13.0),
    "Limonad": (38, 0.1, 0.0, 9.5),
    "Shokoladli milkshake": (130, 3.5, 4.5, 20.0),
    "Issiq shokolad": (90, 3.0, 3.5, 12.0),

    "Espresso": (2, 0.1, 0.0, 0.0),
    "Kapuchino": (40, 2.0, 2.0, 4.0),
    "Latte": (45, 2.2, 2.2, 4.5),
    "Amerikano": (2, 0.1, 0.0, 0.0),
    "Muzli latte": (45, 2.0, 2.0, 5.0),

    "Napoleon + Espresso": (300, 4.0, 18.0, 30.0),
    "Tiramisu + Kapuchino": (280, 5.0, 16.0, 25.0),
    "Shokoladli tort + Latte": (320, 4.5, 16.0, 40.0),
    "2 ta Donut + Amerikano": (300, 4.0, 15.0, 38.0),
    "Makaron seti + Espresso": (350, 6.5, 17.0, 48.0),
    "Ezoklair + Kapuchino": (300, 5.0, 18.0, 30.0),
    "Shokoladli muffin + Limonad": (280, 4.0, 14.0, 40.0),
    "Chak-chak + Qora kofe": (320, 5.0, 13.0, 48.0),
    "Pechenye to'plami + Milkshake": (380, 5.0, 20.0, 48.0),
    "Rezavorli tort + Smuzi": (260, 3.5, 12.0, 35.0),

    "Chizburger": (280, 15.0, 16.0, 22.0),
    "Dabl burger": (320, 19.0, 20.0, 23.0),
    "BBQ tovuq pitsasi": (260, 12.0, 10.0, 30.0),
    "Margarita pitsa": (250, 11.0, 9.5, 31.0),
    "Pepperoni pitsa": (270, 12.5, 12.0, 29.0),
    "Kartoshka fri": (310, 3.5, 15.0, 40.0),
    "Tovuq striplari": (250, 18.0, 13.0, 14.0),
    "Bufalo qanotlari": (280, 20.0, 19.0, 6.0),
    "Klub sendvich": (240, 14.0, 10.0, 24.0),
    "Rostbif sendvich": (220, 15.0, 8.0, 22.0),
    "Meksika tako seti": (200, 10.0, 8.0, 22.0),
    "Tovuq shaurma": (230, 13.0, 9.0, 25.0),
}

# uz nomi -> (miqdor_uz, miqdor_ru, miqdor_en)
QUANTITY = {
    "Shokoladli tort": ("1.5 kg (10-12 porsiya)", "1.5 кг (10-12 порций)", "1.5 kg (10-12 servings)"),
    "Rezavorli tort": ("1.5 kg (10-12 porsiya)", "1.5 кг (10-12 порций)", "1.5 kg (10-12 servings)"),
    "Nikoh torti": ("5 kg (30-40 porsiya)", "5 кг (30-40 порций)", "5 kg (30-40 servings)"),
    "Cheesecake": ("1.2 kg (8-10 porsiya)", "1.2 кг (8-10 порций)", "1.2 kg (8-10 servings)"),
    "Mevali tart": ("300 gr (1 dona)", "300 г (1 шт.)", "300 g (1 pc)"),

    "Napoleon pirojnoye": ("150 gr (1 dona)", "150 г (1 шт.)", "150 g (1 pc)"),
    "Tiramisu": ("150 gr (1 dona)", "150 г (1 шт.)", "150 g (1 pc)"),
    "Ezoklair": ("80 gr (1 dona)", "80 г (1 шт.)", "80 g (1 pc)"),
    "Dolchinli rulet": ("100 gr (1 dona)", "100 г (1 шт.)", "100 g (1 pc)"),
    "Kruassan": ("70 gr (1 dona)", "70 г (1 шт.)", "70 g (1 pc)"),
    "Belgiya vaflisi": ("150 gr (1 dona)", "150 г (1 шт.)", "150 g (1 pc)"),
    "Cannoli": ("90 gr (1 dona)", "90 г (1 шт.)", "90 g (1 pc)"),

    "Klassik donut": ("70 gr (1 dona)", "70 г (1 шт.)", "70 g (1 pc)"),
    "Shokoladli donut": ("75 gr (1 dona)", "75 г (1 шт.)", "75 g (1 pc)"),
    "Pushti glazurli donut": ("75 gr (1 dona)", "75 г (1 шт.)", "75 g (1 pc)"),

    "Choco-chip pechenye": ("300 gr (12 dona)", "300 г (12 шт.)", "300 g (12 pcs)"),
    "Oatmeal pechenye": ("280 gr (10 dona)", "280 г (10 шт.)", "280 g (10 pcs)"),
    "Assorti pechenye to'plami": ("350 gr (15 dona)", "350 г (15 шт.)", "350 g (15 pcs)"),

    "Qora shokolad 70%": ("100 gr", "100 г", "100 g"),
    "Sut shokoladi yong'oqli": ("100 gr", "100 г", "100 g"),
    "Shokolad konfet to'plami": ("300 gr", "300 г", "300 g"),
    "Shokoladli brauni": ("120 gr (1 dona)", "120 г (1 шт.)", "120 g (1 pc)"),
    "Praline to'plami": ("200 gr", "200 г", "200 g"),

    "Jele konfetlar": ("300 gr", "300 г", "300 g"),
    "Karamel konfet": ("250 gr", "250 г", "250 g"),
    "Marmelad konfetlar": ("250 gr", "250 г", "250 g"),

    "Rangli makaron to'plami": ("12 dona (~180 gr)", "12 шт. (~180 г)", "12 pcs (~180 g)"),
    "Vanil makaron": ("6 dona (~90 gr)", "6 шт. (~90 г)", "6 pcs (~90 g)"),
    "Shokoladli makaron": ("6 dona (~90 gr)", "6 шт. (~90 г)", "6 pcs (~90 g)"),

    "Vanil muzqaymoq": ("500 ml", "500 мл", "500 ml"),
    "Shokoladli muzqaymoq": ("500 ml", "500 мл", "500 ml"),
    "Rezavorli sorbet": ("500 ml", "500 мл", "500 ml"),

    "Halva": ("400 gr", "400 г", "400 g"),
    "Parvarda": ("300 gr", "300 г", "300 g"),
    "Chak-chak": ("400 gr", "400 г", "400 g"),
    "Baklava": ("350 gr", "350 г", "350 g"),

    "Vanil keksi": ("180 gr (6 dona)", "180 г (6 шт.)", "180 g (6 pcs)"),
    "Shokoladli muffin": ("300 gr (6 dona)", "300 г (6 шт.)", "300 g (6 pcs)"),
    "Limonli keks": ("400 gr (1 dona)", "400 г (1 шт.)", "400 g (1 pc)"),
    "Red Velvet keks": ("200 gr (4 dona)", "200 г (4 шт.)", "200 g (4 pcs)"),

    "Apelsin sharbati": ("500 ml", "500 мл", "500 ml"),
    "Qulupnay smuzi": ("400 ml", "400 мл", "400 ml"),
    "Limonad": ("500 ml", "500 мл", "500 ml"),
    "Shokoladli milkshake": ("450 ml", "450 мл", "450 ml"),
    "Issiq shokolad": ("300 ml", "300 мл", "300 ml"),

    "Espresso": ("30 ml", "30 мл", "30 ml"),
    "Kapuchino": ("200 ml", "200 мл", "200 ml"),
    "Latte": ("250 ml", "250 мл", "250 ml"),
    "Amerikano": ("220 ml", "220 мл", "220 ml"),
    "Muzli latte": ("300 ml", "300 мл", "300 ml"),

    "Napoleon + Espresso": ("1 dona + 30 ml", "1 шт. + 30 мл", "1 pc + 30 ml"),
    "Tiramisu + Kapuchino": ("1 dona + 200 ml", "1 шт. + 200 мл", "1 pc + 200 ml"),
    "Shokoladli tort + Latte": ("1 bo'lak + 250 ml", "1 кусок + 250 мл", "1 slice + 250 ml"),
    "2 ta Donut + Amerikano": ("2 dona + 220 ml", "2 шт. + 220 мл", "2 pcs + 220 ml"),
    "Makaron seti + Espresso": ("6 dona + 30 ml", "6 шт. + 30 мл", "6 pcs + 30 ml"),
    "Ezoklair + Kapuchino": ("1 dona + 200 ml", "1 шт. + 200 мл", "1 pc + 200 ml"),
    "Shokoladli muffin + Limonad": ("1 dona + 500 ml", "1 шт. + 500 мл", "1 pc + 500 ml"),
    "Chak-chak + Qora kofe": ("200 gr + 220 ml", "200 г + 220 мл", "200 g + 220 ml"),
    "Pechenye to'plami + Milkshake": ("200 gr + 450 ml", "200 г + 450 мл", "200 g + 450 ml"),
    "Rezavorli tort + Smuzi": ("1 bo'lak + 400 ml", "1 кусок + 400 мл", "1 slice + 400 ml"),

    "Chizburger": ("220 gr (1 dona)", "220 г (1 шт.)", "220 g (1 pc)"),
    "Dabl burger": ("320 gr (1 dona)", "320 г (1 шт.)", "320 g (1 pc)"),
    "BBQ tovuq pitsasi": ("32 sm (4 bo'lak)", "32 см (4 куска)", "32 cm (4 slices)"),
    "Margarita pitsa": ("30 sm (4 bo'lak)", "30 см (4 куска)", "30 cm (4 slices)"),
    "Pepperoni pitsa": ("32 sm (6 bo'lak)", "32 см (6 кусков)", "32 cm (6 slices)"),
    "Kartoshka fri": ("250 gr", "250 г", "250 g"),
    "Tovuq striplari": ("280 gr (6 dona)", "280 г (6 шт.)", "280 g (6 pcs)"),
    "Bufalo qanotlari": ("350 gr (8 dona)", "350 г (8 шт.)", "350 g (8 pcs)"),
    "Klub sendvich": ("260 gr (1 dona)", "260 г (1 шт.)", "260 g (1 pc)"),
    "Rostbif sendvich": ("230 gr (1 dona)", "230 г (1 шт.)", "230 g (1 pc)"),
    "Meksika tako seti": ("3 dona (~270 gr)", "3 шт. (~270 г)", "3 pcs (~270 g)"),
    "Tovuq shaurma": ("300 gr (1 dona)", "300 г (1 шт.)", "300 g (1 pc)"),
}

# key -> (name_uz, name_ru, name_en)
CATEGORIES = [
    ("tort", "Tortlar", "Торты", "Cakes"),
    ("pirojnoye", "Pirojnoye va desertlar", "Пирожные и десерты", "Pastries & Desserts"),
    ("donut", "Donutlar", "Пончики", "Donuts"),
    ("pechenye", "Pechenye", "Печенье", "Cookies"),
    ("shokolad", "Shokoladlar", "Шоколад", "Chocolate"),
    ("konfet", "Konfetlar", "Конфеты", "Candy"),
    ("makaron", "Makaronlar", "Макаруны", "Macarons"),
    ("muzqaymoq", "Muzqaymoq", "Мороженое", "Ice Cream"),
    ("milliy", "Milliy shirinliklar", "Национальные сладости", "National Sweets"),
    ("keks", "Keks va muffinlar", "Кексы и маффины", "Cupcakes & Muffins"),
    ("ichimlik", "Ichimliklar", "Напитки", "Drinks"),
    ("qahva", "Qahva", "Кофе", "Coffee"),
    ("fastfud", "Fastfud", "Фастфуд", "Fast Food"),
    ("combo", "Haftalik chegirmalar", "Скидки недели", "Weekly Deals"),
]

# Each entry: cat_key, price, discount, in_stock, rating, image,
#   (name_uz, desc_uz, comp_uz), (name_ru, desc_ru, comp_ru), (name_en, desc_en, comp_en)
PRODUCTS = [
    ("tort", 250000, 210000, True, 4.8, A,
     ("Shokoladli tort", "Uch qavatli, krem bilan", "Bug'doy uni, shakar, tuxum, kakao kukuni, sariyog', sut, ishlov berilgan shokolad, pishirish kukuni"),
     ("Шоколадный торт", "Трёхслойный, с кремом", "Пшеничная мука, сахар, яйца, какао-порошок, сливочное масло, молоко, шоколад, разрыхлитель"),
     ("Chocolate Cake", "Three layers, with cream", "Wheat flour, sugar, eggs, cocoa powder, butter, milk, chocolate, baking powder")),
    ("tort", 280000, None, True, 4.7, AB,
     ("Rezavorli tort", "Yovvoyi rezavorlar bilan bezatilgan", "Bug'doy uni, shakar, tuxum, sariyog', qaymoq krem, mavsumiy rezavorlar (qulupnay, malina, ko'k smorodina)"),
     ("Ягодный торт", "Украшен лесными ягодами", "Пшеничная мука, сахар, яйца, сливочное масло, сливочный крем, сезонные ягоды (клубника, малина, смородина)"),
     ("Berry Cake", "Decorated with wild berries", "Wheat flour, sugar, eggs, butter, cream, seasonal berries (strawberry, raspberry, blackcurrant)")),
    ("tort", 450000, None, True, 4.9, P,
     ("Nikoh torti", "Oq krem, ko'p qavatli", "Bug'doy uni, shakar, tuxum, sariyog', vanil ekstrakti, oq shokolad, mastika bezak"),
     ("Свадебный торт", "Белый крем, многоярусный", "Пшеничная мука, сахар, яйца, сливочное масло, экстракт ванили, белый шоколад, мастика"),
     ("Wedding Cake", "White cream, multi-tier", "Wheat flour, sugar, eggs, butter, vanilla extract, white chocolate, fondant decoration")),
    ("tort", 65000, 55000, True, 4.8, NI3,
     ("Cheesecake", "Nyu-York uslubida, tvorojli krem", "Krem pishloq, shakar, tuxum, gallet pechenye, sariyog'"),
     ("Чизкейк", "Нью-Йоркский стиль, творожный крем", "Сливочный сыр, сахар, яйца, печенье, сливочное масло"),
     ("Cheesecake", "New York style, cream cheese filling", "Cream cheese, sugar, eggs, biscuit crust, butter")),
    ("tort", 28000, None, True, 4.6, NI16,
     ("Mevali tart", "Mavsumiy mevalar bilan, individual", "Un, sariyog', qaymoq krem, mavsumiy mevalar"),
     ("Фруктовый тарт", "С сезонными фруктами, порционный", "Мука, сливочное масло, сливочный крем, сезонные фрукты"),
     ("Fruit Tart", "With seasonal fruit, individual size", "Flour, butter, cream filling, seasonal fruit")),

    ("pirojnoye", 18000, None, True, 4.6, Y,
     ("Napoleon pirojnoye", "Qatlamli xamir, vanil krem", "Qatlamli xamir (un, sariyog', tuxum), vanil krem (sut, shakar, tuxum sarig'i, kraxmal)"),
     ("Наполеон", "Слоёное тесто, ванильный крем", "Слоёное тесто (мука, масло, яйца), ванильный крем (молоко, сахар, желток, крахмал)"),
     ("Napoleon Pastry", "Puff pastry, vanilla cream", "Puff pastry (flour, butter, eggs), vanilla cream (milk, sugar, egg yolk, starch)")),
    ("pirojnoye", 32000, 27000, True, 4.8, Q,
     ("Tiramisu", "Kofe va mascarpone bilan", "Mascarpone pishloq, savoyardi pechenye, espresso kofe, kakao kukuni, tuxum, shakar"),
     ("Тирамису", "С кофе и маскарпоне", "Сыр маскарпоне, печенье савоярди, кофе эспрессо, какао-порошок, яйца, сахар"),
     ("Tiramisu", "With coffee and mascarpone", "Mascarpone cheese, savoiardi biscuits, espresso coffee, cocoa powder, eggs, sugar")),
    ("pirojnoye", 16000, None, True, 4.5, T,
     ("Ezoklair", "Shokolad glazur bilan", "Zavarnoy xamir (un, sariyog', tuxum), vanil krem, shokolad glazur"),
     ("Эклер", "С шоколадной глазурью", "Заварное тесто (мука, масло, яйца), ванильный крем, шоколадная глазурь"),
     ("Eclair", "With chocolate glaze", "Choux pastry (flour, butter, eggs), vanilla cream, chocolate glaze")),
    ("pirojnoye", 16000, None, True, 4.6, NI1,
     ("Dolchinli rulet", "Yumshoq xamir, dolchinli krem bilan", "Bug'doy uni, sariyog', shakar, dolchin, tuxum, krem pishloq glazur"),
     ("Булочка с корицей", "Мягкое тесто с корично-масляной начинкой", "Пшеничная мука, сливочное масло, сахар, корица, яйца, глазурь из сливочного сыра"),
     ("Cinnamon Roll", "Soft dough with cinnamon-butter filling", "Wheat flour, butter, sugar, cinnamon, eggs, cream cheese glaze")),
    ("pirojnoye", 14000, None, True, 4.5, NI17,
     ("Kruassan", "Frantsuz uslubida, varaqlangan", "Bug'doy uni, sariyog', xamirturush, tuz, shakar"),
     ("Круассан", "Французский, слоёный", "Пшеничная мука, сливочное масло, дрожжи, соль, сахар"),
     ("Croissant", "French-style, flaky layers", "Wheat flour, butter, yeast, salt, sugar")),
    ("pirojnoye", 24000, None, True, 4.6, NI4,
     ("Belgiya vaflisi", "Asal va rezavorlar bilan", "Un, tuxum, sut, sariyog', shakar, asal, rezavorlar"),
     ("Бельгийская вафля", "С мёдом и ягодами", "Мука, яйца, молоко, сливочное масло, сахар, мёд, ягоды"),
     ("Belgian Waffle", "With honey and berries", "Flour, eggs, milk, butter, sugar, honey, berries")),
    ("pirojnoye", 21000, None, True, 4.7, NI19,
     ("Cannoli", "Sitsiliya uslubida, rikotta krem", "Xamir naycha, rikotta pishloq, shakar, shokolad bo'lakchalari"),
     ("Канноли", "Сицилийский стиль, крем рикотта", "Хрустящая трубочка, сыр рикотта, сахар, кусочки шоколада"),
     ("Cannoli", "Sicilian style, ricotta cream", "Crispy pastry tube, ricotta cheese, sugar, chocolate chips")),

    ("donut", 15000, None, True, 4.4, F,
     ("Klassik donut", "Shakar glazur bilan", "Bug'doy uni, shakar, xamirturush, sut, tuxum, o'simlik moyi, shakar glazur"),
     ("Классический пончик", "С сахарной глазурью", "Пшеничная мука, сахар, дрожжи, молоко, яйца, растительное масло, сахарная глазурь"),
     ("Classic Donut", "With sugar glaze", "Wheat flour, sugar, yeast, milk, eggs, vegetable oil, sugar glaze")),
    ("donut", 17000, 14000, True, 4.6, NI18,
     ("Shokoladli donut", "Shokolad glazur, sprinkle", "Bug'doy uni, shakar, xamirturush, sut, tuxum, shokolad glazur, rangli sprinkle"),
     ("Шоколадный пончик", "Шоколадная глазурь, посыпка", "Пшеничная мука, сахар, дрожжи, молоко, яйца, шоколадная глазурь, цветная посыпка"),
     ("Chocolate Donut", "Chocolate glaze, sprinkles", "Wheat flour, sugar, yeast, milk, eggs, chocolate glaze, colorful sprinkles")),
    ("donut", 17000, None, True, 4.5, F,
     ("Pushti glazurli donut", "Meva ta'mi glazur", "Bug'doy uni, shakar, xamirturush, sut, tuxum, meva ta'mli glazur (qulupnay)"),
     ("Пончик с розовой глазурью", "Фруктовая глазурь", "Пшеничная мука, сахар, дрожжи, молоко, яйца, фруктовая глазурь (клубника)"),
     ("Pink Glazed Donut", "Fruit-flavored glaze", "Wheat flour, sugar, yeast, milk, eggs, fruit glaze (strawberry)")),

    ("pechenye", 32000, None, True, 4.6, G,
     ("Choco-chip pechenye", "12 dona quti", "Bug'doy uni, sariyog', jigarrang shakar, tuxum, shokolad bo'lakchalari, vanil"),
     ("Печенье с шоколадной крошкой", "Упаковка 12 шт.", "Пшеничная мука, сливочное масло, коричневый сахар, яйца, кусочки шоколада, ваниль"),
     ("Choco-Chip Cookies", "Box of 12", "Wheat flour, butter, brown sugar, eggs, chocolate chips, vanilla")),
    ("pechenye", 28000, 24000, True, 4.4, G,
     ("Oatmeal pechenye", "Yormali, asal bilan", "Suli yormasi, bug'doy uni, asal, sariyog', mayiz, tarkan"),
     ("Овсяное печенье", "С овсянкой и мёдом", "Овсяные хлопья, пшеничная мука, мёд, сливочное масло, изюм, корица"),
     ("Oatmeal Cookies", "With oats and honey", "Oat flakes, wheat flour, honey, butter, raisins, cinnamon")),
    ("pechenye", 35000, None, True, 4.5, G,
     ("Assorti pechenye to'plami", "Turli shakldagi pechenyelar", "Bug'doy uni, sariyog', shakar, tuxum, vanil — turli shakl va ta'mlar aralashmasi"),
     ("Ассорти печенья", "Печенье разной формы", "Пшеничная мука, сливочное масло, сахар, яйца, ваниль — смесь разных форм и вкусов"),
     ("Assorted Cookie Set", "Cookies of different shapes", "Wheat flour, butter, sugar, eggs, vanilla — mix of shapes and flavors")),

    ("shokolad", 30000, None, True, 4.7, J,
     ("Qora shokolad 70%", "100gr plitka", "Kakao massasi (70%), kakao moyi, shakar, kakao kukuni"),
     ("Тёмный шоколад 70%", "Плитка 100г", "Какао тёртое (70%), какао-масло, сахар, какао-порошок"),
     ("Dark Chocolate 70%", "100g bar", "Cocoa mass (70%), cocoa butter, sugar, cocoa powder")),
    ("shokolad", 27000, None, True, 4.5, V,
     ("Sut shokoladi yong'oqli", "100gr", "Sut kukuni, kakao moyi, shakar, yeryong'oq/findiq, kakao massasi"),
     ("Молочный шоколад с орехами", "100г", "Сухое молоко, какао-масло, сахар, арахис/фундук, какао тёртое"),
     ("Milk Chocolate with Nuts", "100g", "Milk powder, cocoa butter, sugar, peanuts/hazelnuts, cocoa mass")),
    ("shokolad", 45000, 39000, True, 4.7, S,
     ("Shokolad konfet to'plami", "Aralash quti, 300gr", "Sut va qora shokolad, praline, yong'oq, meva to'ldirmalari"),
     ("Набор шоколадных конфет", "Ассорти, 300г", "Молочный и тёмный шоколад, пралине, орехи, фруктовые начинки"),
     ("Chocolate Candy Assortment", "Mixed box, 300g", "Milk and dark chocolate, praline, nuts, fruit fillings")),
    ("shokolad", 20000, None, True, 4.7, E,
     ("Shokoladli brauni", "Zich va yumshoq, yong'oqli", "Qora shokolad, sariyog', shakar, tuxum, un, yong'oq"),
     ("Шоколадный брауни", "Плотный и мягкий, с орехами", "Тёмный шоколад, сливочное масло, сахар, яйца, мука, орехи"),
     ("Chocolate Brownie", "Dense and fudgy, with walnuts", "Dark chocolate, butter, sugar, eggs, flour, walnuts")),
    ("shokolad", 48000, 42000, True, 4.8, CB3,
     ("Praline to'plami", "Yong'oqli praline konfetlar, 200gr", "Shokolad, findiq, shakar, sariyog'"),
     ("Набор пралине", "Ореховые конфеты пралине, 200г", "Шоколад, фундук, сахар, сливочное масло"),
     ("Praline Box", "Hazelnut praline chocolates, 200g", "Chocolate, hazelnuts, sugar, butter")),

    ("konfet", 25000, None, True, 4.3, I_,
     ("Jele konfetlar", "Meva ta'mi, 300gr", "Shakar, glyukoza siropi, jelatin, meva sharbati kontsentrati, limon kislotasi"),
     ("Желейные конфеты", "Фруктовый вкус, 300г", "Сахар, глюкозный сироп, желатин, концентрат фруктового сока, лимонная кислота"),
     ("Jelly Candy", "Fruit flavor, 300g", "Sugar, glucose syrup, gelatin, fruit juice concentrate, citric acid")),
    ("konfet", 22000, None, True, 4.2, I_,
     ("Karamel konfet", "Yumshoq karamel, 250gr", "Shakar, glyukoza siropi, sariyog', qaymoq, vanil"),
     ("Карамельные конфеты", "Мягкая карамель, 250г", "Сахар, глюкозный сироп, сливочное масло, сливки, ваниль"),
     ("Caramel Candy", "Soft caramel, 250g", "Sugar, glucose syrup, butter, cream, vanilla")),
    ("konfet", 24000, None, True, 4.3, I_,
     ("Marmelad konfetlar", "Rangli, 250gr", "Shakar, pektin, meva sharbati, limon kislotasi, tabiiy bo'yoqlar"),
     ("Мармеладные конфеты", "Разноцветные, 250г", "Сахар, пектин, фруктовый сок, лимонная кислота, натуральные красители"),
     ("Marmalade Candy", "Colorful, 250g", "Sugar, pectin, fruit juice, citric acid, natural colorings")),

    ("makaron", 38000, None, True, 4.8, H,
     ("Rangli makaron to'plami", "12 dona, aralash ta'm", "Bodom uni, quandagi oqsil, shakar, pishirish kukuni, turli ta'mli kremlar"),
     ("Набор цветных макарун", "12 шт., ассорти вкусов", "Миндальная мука, яичный белок, сахар, разрыхлитель, кремы разных вкусов"),
     ("Colorful Macaron Set", "12 pcs, assorted flavors", "Almond flour, egg white, sugar, baking powder, assorted flavored fillings")),
    ("makaron", 22000, None, True, 4.6, NI15,
     ("Vanil makaron", "6 dona", "Bodom uni, tuxum oqsili, shakar, vanil kremi"),
     ("Ванильные макаруны", "6 шт.", "Миндальная мука, яичный белок, сахар, ванильный крем"),
     ("Vanilla Macarons", "6 pcs", "Almond flour, egg white, sugar, vanilla cream")),
    ("makaron", 22000, 19000, True, 4.7, U,
     ("Shokoladli makaron", "6 dona", "Bodom uni, tuxum oqsili, shakar, shokolad ganash"),
     ("Шоколадные макаруны", "6 шт.", "Миндальная мука, яичный белок, сахар, шоколадный ганаш"),
     ("Chocolate Macarons", "6 pcs", "Almond flour, egg white, sugar, chocolate ganache")),

    ("muzqaymoq", 28000, None, True, 4.5, K,
     ("Vanil muzqaymoq", "500ml", "Sut, qaymoq, shakar, tuxum sarig'i, tabiiy vanil"),
     ("Ванильное мороженое", "500мл", "Молоко, сливки, сахар, желток, натуральная ваниль"),
     ("Vanilla Ice Cream", "500ml", "Milk, cream, sugar, egg yolk, natural vanilla")),
    ("muzqaymoq", 28000, None, True, 4.6, L,
     ("Shokoladli muzqaymoq", "500ml", "Sut, qaymoq, shakar, kakao, shokolad bo'lakchalari"),
     ("Шоколадное мороженое", "500мл", "Молоко, сливки, сахар, какао, кусочки шоколада"),
     ("Chocolate Ice Cream", "500ml", "Milk, cream, sugar, cocoa, chocolate pieces")),
    ("muzqaymoq", 30000, None, True, 4.4, L,
     ("Rezavorli sorbet", "500ml, sut mahsulotsiz", "Meva pyuresi (rezavorlar), shakar, suv, limon sharbati"),
     ("Ягодный сорбет", "500мл, без молочных продуктов", "Фруктовое пюре (ягоды), сахар, вода, лимонный сок"),
     ("Berry Sorbet", "500ml, dairy-free", "Fruit puree (berries), sugar, water, lemon juice")),

    ("milliy", 32000, None, True, 4.6, AA,
     ("Halva", "An'anaviy, yong'oqli, 400gr", "Kunjut yog'i, shakar siropi, sovun ildizi ekstrakti, yong'oq"),
     ("Халва", "Традиционная, с орехами, 400г", "Кунжутное масло, сахарный сироп, экстракт мыльного корня, орехи"),
     ("Halva", "Traditional, with nuts, 400g", "Sesame oil, sugar syrup, soapwort root extract, nuts")),
    ("milliy", 20000, None, True, 4.4, U,
     ("Parvarda", "Qand asosida tayyorlangan, 300gr", "Shakar, suv, limon kislotasi, vanil"),
     ("Парварда", "На основе сахара, 300г", "Сахар, вода, лимонная кислота, ваниль"),
     ("Parvarda", "Sugar-based, 300g", "Sugar, water, citric acid, vanilla")),
    ("milliy", 26000, None, True, 4.5, NI17,
     ("Chak-chak", "Asal bilan, 400gr", "Un, tuxum, asal, o'simlik moyi (qovurish uchun)"),
     ("Чак-чак", "С мёдом, 400г", "Мука, яйца, мёд, растительное масло (для жарки)"),
     ("Chak-Chak", "With honey, 400g", "Flour, eggs, honey, vegetable oil (for frying)")),
    ("milliy", 34000, None, True, 4.7, NI17,
     ("Baklava", "Yong'oqli, asal siropida", "Yupqa xamir varaqlari, yong'oq, asal, sariyog'"),
     ("Пахлава", "Ореховая, в медовом сиропе", "Тонкие слои теста, орехи, мёд, сливочное масло"),
     ("Baklava", "With nuts, in honey syrup", "Thin pastry layers, nuts, honey, butter")),

    ("keks", 24000, None, True, 4.5, D,
     ("Vanil keksi", "Mini keks, 6 dona", "Bug'doy uni, sariyog', shakar, tuxum, vanil, pishirish kukuni"),
     ("Ванильный кекс", "Мини-кекс, 6 шт.", "Пшеничная мука, сливочное масло, сахар, яйца, ваниль, разрыхлитель"),
     ("Vanilla Cupcakes", "Mini, 6 pcs", "Wheat flour, butter, sugar, eggs, vanilla, baking powder")),
    ("keks", 26000, 22000, True, 4.6, NI19,
     ("Shokoladli muffin", "6 dona", "Bug'doy uni, kakao, shakar, tuxum, sariyog', shokolad bo'lakchalari"),
     ("Шоколадный маффин", "6 шт.", "Пшеничная мука, какао, сахар, яйца, сливочное масло, кусочки шоколада"),
     ("Chocolate Muffins", "6 pcs", "Wheat flour, cocoa, sugar, eggs, butter, chocolate chips")),
    ("keks", 27000, None, True, 4.5, AB,
     ("Limonli keks", "Limon glazur bilan", "Bug'doy uni, sariyog', shakar, tuxum, limon qobig'i va sharbati, glazur"),
     ("Лимонный кекс", "С лимонной глазурью", "Пшеничная мука, сливочное масло, сахар, яйца, цедра и сок лимона, глазурь"),
     ("Lemon Cake", "With lemon glaze", "Wheat flour, butter, sugar, eggs, lemon zest and juice, glaze")),
    ("keks", 23000, None, True, 4.6, D,
     ("Red Velvet keks", "Qizil pishiriq, cream cheese krem", "Bug'doy uni, kakao, qizil bo'yoq, tuxum, sariyog', krem pishloq"),
     ("Кекс Red Velvet", "Красный бисквит, крем чиз", "Пшеничная мука, какао, пищевой краситель, яйца, масло, сливочный сыр"),
     ("Red Velvet Cupcake", "Red sponge, cream cheese frosting", "Wheat flour, cocoa, food coloring, eggs, butter, cream cheese")),

    ("ichimlik", 18000, None, True, 4.6, DR2,
     ("Apelsin sharbati", "Yangi siqilgan, 500ml", "100% apelsin sharbati, konservantsiz"),
     ("Апельсиновый сок", "Свежевыжатый, 500мл", "100% апельсиновый сок, без консервантов"),
     ("Orange Juice", "Freshly squeezed, 500ml", "100% orange juice, no preservatives")),
    ("ichimlik", 20000, None, True, 4.5, DR7,
     ("Qulupnay smuzi", "Tabiiy, 400ml", "Qulupnay, banan, tabiiy yogurt, asal"),
     ("Клубничный смузи", "Натуральный, 400мл", "Клубника, банан, натуральный йогурт, мёд"),
     ("Strawberry Smoothie", "Natural, 400ml", "Strawberry, banana, natural yogurt, honey")),
    ("ichimlik", 15000, None, True, 4.4, DR1,
     ("Limonad", "Uy usulida, 500ml", "Suv, limon sharbati, shakar, yalpiz"),
     ("Лимонад", "Домашний, 500мл", "Вода, лимонный сок, сахар, мята"),
     ("Lemonade", "Homemade, 500ml", "Water, lemon juice, sugar, mint")),
    ("ichimlik", 22000, 18000, True, 4.7, L,
     ("Shokoladli milkshake", "450ml", "Sut, muzqaymoq, shokolad siropi, qaymoq"),
     ("Шоколадный милкшейк", "450мл", "Молоко, мороженое, шоколадный сироп, сливки"),
     ("Chocolate Milkshake", "450ml", "Milk, ice cream, chocolate syrup, cream")),
    ("ichimlik", 19000, None, True, 4.6, CF3,
     ("Issiq shokolad", "300ml, qaymoq bilan", "Sut, qora shokolad, shakar, qaymoq"),
     ("Горячий шоколад", "300мл, со сливками", "Молоко, тёмный шоколад, сахар, сливки"),
     ("Hot Chocolate", "300ml, with whipped cream", "Milk, dark chocolate, sugar, cream")),

    ("qahva", 12000, None, True, 4.6, CF1,
     ("Espresso", "30ml, klassik", "100% arabika kofe donlari"),
     ("Эспрессо", "30мл, классика", "100% зёрна арабики"),
     ("Espresso", "30ml, classic", "100% arabica coffee beans")),
    ("qahva", 18000, None, True, 4.7, CF4,
     ("Kapuchino", "200ml, sut ko'pigi bilan", "Espresso, bug'langan sut, sut ko'pigi"),
     ("Капучино", "200мл, с молочной пенкой", "Эспрессо, взбитое молоко, молочная пенка"),
     ("Cappuccino", "200ml, with milk foam", "Espresso, steamed milk, milk foam")),
    ("qahva", 20000, None, True, 4.6, CF3,
     ("Latte", "250ml, yumshoq ta'm", "Espresso, ko'p sut, ozgina sut ko'pigi"),
     ("Латте", "250мл, мягкий вкус", "Эспрессо, много молока, немного молочной пенки"),
     ("Latte", "250ml, smooth taste", "Espresso, lots of milk, a little milk foam")),
    ("qahva", 14000, None, True, 4.4, CF2,
     ("Amerikano", "220ml", "Espresso, issiq suv"),
     ("Американо", "220мл", "Эспрессо, горячая вода"),
     ("Americano", "220ml", "Espresso, hot water")),
    ("qahva", 22000, None, True, 4.6, N,
     ("Muzli latte", "300ml, sovuq ichimlik", "Espresso, sovuq sut, muz"),
     ("Айс латте", "300мл, холодный напиток", "Эспрессо, холодное молоко, лёд"),
     ("Iced Latte", "300ml, cold drink", "Espresso, cold milk, ice")),

    ("fastfud", 32000, None, True, 4.7, FF1,
     ("Chizburger", "Mol go'shti kotleti, erigan pishloq, yangi sabzavotlar", "Bulochka, mol go'shti, pishloq, pomidor, salat barglari, piyoz, sous"),
     ("Чизбургер", "Говяжья котлета, плавленый сыр, свежие овощи", "Булочка, говядина, сыр, помидор, листья салата, лук, соус"),
     ("Cheeseburger", "Beef patty, melted cheese, fresh vegetables", "Bun, beef, cheese, tomato, lettuce, onion, sauce")),
    ("fastfud", 42000, 36000, True, 4.8, FF2,
     ("Dabl burger", "Ikki qavat go'sht kotleti, bekon, pishloq", "Bulochka, 2x mol go'shti, bekon, pishloq, sous, tuzlangan bodring"),
     ("Дабл бургер", "Двойная котлета, бекон, сыр", "Булочка, 2x говядина, бекон, сыр, соус, маринованный огурец"),
     ("Double Burger", "Double beef patty, bacon, cheese", "Bun, 2x beef, bacon, cheese, sauce, pickles")),
    ("fastfud", 55000, None, True, 4.6, FF3,
     ("BBQ tovuq pitsasi", "32 sm, tovuq, BBQ sous, qizil piyoz", "Xamir, pomidor sousi, mocarella, tovuq go'shti, BBQ sous, qizil piyoz"),
     ("Пицца BBQ с курицей", "32 см, курица, соус BBQ, красный лук", "Тесто, томатный соус, моцарелла, курица, соус BBQ, красный лук"),
     ("BBQ Chicken Pizza", "32 cm, chicken, BBQ sauce, red onion", "Dough, tomato sauce, mozzarella, chicken, BBQ sauce, red onion")),
    ("fastfud", 48000, None, True, 4.7, FF4,
     ("Margarita pitsa", "Klassik, mocarella va rayhon bilan", "Xamir, pomidor sousi, mocarella, rayhon, zaytun moyi"),
     ("Пицца Маргарита", "Классика, с моцареллой и базиликом", "Тесто, томатный соус, моцарелла, базилик, оливковое масло"),
     ("Margherita Pizza", "Classic, with mozzarella and basil", "Dough, tomato sauce, mozzarella, basil, olive oil")),
    ("fastfud", 52000, 44000, True, 4.8, FF5,
     ("Pepperoni pitsa", "Achchiq pepperoni kolbasa, mo'l pishloq", "Xamir, pomidor sousi, mocarella, pepperoni kolbasa"),
     ("Пицца Пепперони", "Острая пепперони, много сыра", "Тесто, томатный соус, моцарелла, колбаса пепперони"),
     ("Pepperoni Pizza", "Spicy pepperoni, extra cheese", "Dough, tomato sauce, mozzarella, pepperoni")),
    ("fastfud", 18000, None, True, 4.6, FF6,
     ("Kartoshka fri", "Xrustyash, tuzlangan, ketchup bilan", "Kartoshka, kungaboqar moyi, tuz"),
     ("Картофель фри", "Хрустящий, солёный, с кетчупом", "Картофель, подсолнечное масло, соль"),
     ("French Fries", "Crispy, salted, served with ketchup", "Potato, sunflower oil, salt")),
    ("fastfud", 36000, None, True, 4.7, FF7,
     ("Tovuq striplari", "Panirovkada qovurilgan, sous bilan", "Tovuq filesi, panirovka, tuxum, sous"),
     ("Куриные стрипсы", "Обжаренные в панировке, с соусом", "Куриное филе, панировка, яйцо, соус"),
     ("Chicken Strips", "Breaded and fried, served with sauce", "Chicken fillet, breadcrumbs, egg, sauce")),
    ("fastfud", 45000, 38000, True, 4.7, FF8,
     ("Bufalo qanotlari", "Achchiq bufalo sous, sovuq sous bilan", "Tovuq qanotlari, bufalo sous, sarimsoq, sovuq sous"),
     ("Крылышки Баффало", "Острый соус баффало, с холодным соусом", "Куриные крылышки, соус баффало, чеснок, холодный соус"),
     ("Buffalo Wings", "Spicy buffalo sauce, served with dip", "Chicken wings, buffalo sauce, garlic, cool dip")),
    ("fastfud", 34000, None, True, 4.6, FF9,
     ("Klub sendvich", "Uch qavat, tovuq, bekon, sabzavotlar", "Tost non, tovuq go'shti, bekon, pomidor, salat barglari, mayonez"),
     ("Клаб сэндвич", "Три слоя, курица, бекон, овощи", "Тост, курица, бекон, помидор, листья салата, майонез"),
     ("Club Sandwich", "Triple-decker with chicken, bacon, veggies", "Toast bread, chicken, bacon, tomato, lettuce, mayo")),
    ("fastfud", 33000, None, True, 4.5, FF10,
     ("Rostbif sendvich", "Yupqa kesilgan mol go'shti, yangi sabzavotlar", "Bagett non, rostbif, pomidor, salat barglari, sous"),
     ("Сэндвич с ростбифом", "Тонко нарезанная говядина, свежие овощи", "Багет, ростбиф, помидор, листья салата, соус"),
     ("Roast Beef Sandwich", "Thin-sliced beef, fresh vegetables", "Baguette, roast beef, tomato, lettuce, sauce")),
    ("fastfud", 30000, None, True, 4.6, FF11,
     ("Meksika tako seti", "3 dona, mol go'shti, achchiq sous", "Makkajo'xori tortilya, mol go'shti, piyoz, koriandr, laym"),
     ("Мексиканские тако", "3 шт., говядина, острый соус", "Кукурузная тортилья, говядина, лук, кинза, лайм"),
     ("Mexican Tacos", "3 pieces, beef, spicy sauce", "Corn tortilla, beef, onion, cilantro, lime")),
    ("fastfud", 35000, 29000, True, 4.8, FF12,
     ("Tovuq shaurma", "Lavashda, sabzavotlar va sous bilan", "Lavash, tovuq go'shti, karam, sabzi, sous"),
     ("Куриная шаурма", "В лаваше, с овощами и соусом", "Лаваш, курица, капуста, морковь, соус"),
     ("Chicken Shawarma", "In flatbread, with vegetables and sauce", "Flatbread, chicken, cabbage, carrot, sauce")),

    ("combo", 30000, 16500, True, 4.8, Y,
     ("Napoleon + Espresso", "Kombinatsiya: 1 ta Napoleon pirojnoye + 1 ta espresso", "Napoleon pirojnoye (qatlamli xamir, vanil krem) + espresso (arabika)"),
     ("Наполеон + Эспрессо", "Комбо: 1 Наполеон + 1 эспрессо", "Наполеон (слоёное тесто, ванильный крем) + эспрессо (арабика)"),
     ("Napoleon + Espresso", "Combo: 1 Napoleon pastry + 1 espresso", "Napoleon (puff pastry, vanilla cream) + espresso (arabica)")),
    ("combo", 50000, 27500, True, 4.9, Q,
     ("Tiramisu + Kapuchino", "Kombinatsiya: 1 ta tiramisu + 1 ta kapuchino", "Tiramisu (mascarpone, kofe, kakao) + kapuchino (espresso, sut ko'pigi)"),
     ("Тирамису + Капучино", "Комбо: 1 тирамису + 1 капучино", "Тирамису (маскарпоне, кофе, какао) + капучино (эспрессо, молочная пенка)"),
     ("Tiramisu + Cappuccino", "Combo: 1 tiramisu + 1 cappuccino", "Tiramisu (mascarpone, coffee, cocoa) + cappuccino (espresso, milk foam)")),
    ("combo", 45000, 24500, True, 4.7, A,
     ("Shokoladli tort + Latte", "Kombinatsiya: tort bo'lagi + 1 ta latte", "Shokoladli tort bo'lagi + latte (espresso, sut)"),
     ("Шоколадный торт + Латте", "Комбо: кусок торта + 1 латте", "Кусок шоколадного торта + латте (эспрессо, молоко)"),
     ("Chocolate Cake + Latte", "Combo: cake slice + 1 latte", "Chocolate cake slice + latte (espresso, milk)")),
    ("combo", 40000, 22000, True, 4.6, F,
     ("2 ta Donut + Amerikano", "Kombinatsiya: 2 ta donut + 1 ta amerikano", "Klassik va shokoladli donut + amerikano"),
     ("2 Пончика + Американо", "Комбо: 2 пончика + 1 американо", "Классический и шоколадный пончик + американо"),
     ("2 Donuts + Americano", "Combo: 2 donuts + 1 americano", "Classic and chocolate donut + americano")),
    ("combo", 48000, 26000, True, 4.8, H,
     ("Makaron seti + Espresso", "Kombinatsiya: 6 dona makaron + 1 ta espresso", "Aralash ta'mli makaronlar + espresso"),
     ("Набор макарун + Эспрессо", "Комбо: 6 макарун + 1 эспрессо", "Ассорти макарун + эспрессо"),
     ("Macaron Set + Espresso", "Combo: 6 macarons + 1 espresso", "Assorted macarons + espresso")),
    ("combo", 34000, 18500, True, 4.6, T,
     ("Ezoklair + Kapuchino", "Kombinatsiya: 1 ta ezoklair + 1 ta kapuchino", "Ezoklair (zavarnoy xamir, vanil krem) + kapuchino"),
     ("Эклер + Капучино", "Комбо: 1 эклер + 1 капучино", "Эклер (заварное тесто, ванильный крем) + капучино"),
     ("Eclair + Cappuccino", "Combo: 1 eclair + 1 cappuccino", "Eclair (choux pastry, vanilla cream) + cappuccino")),
    ("combo", 38000, 21000, True, 4.5, NI19,
     ("Shokoladli muffin + Limonad", "Kombinatsiya: 1 ta muffin + 1 ta limonad", "Shokoladli muffin + uy usulida limonad"),
     ("Шоколадный маффин + Лимонад", "Комбо: 1 маффин + 1 лимонад", "Шоколадный маффин + домашний лимонад"),
     ("Chocolate Muffin + Lemonade", "Combo: 1 muffin + 1 lemonade", "Chocolate muffin + homemade lemonade")),
    ("combo", 42000, 23000, True, 4.6, NI17,
     ("Chak-chak + Qora kofe", "Kombinatsiya: chak-chak porsiyasi + 1 ta amerikano", "Chak-chak (un, asal) + amerikano"),
     ("Чак-чак + Чёрный кофе", "Комбо: порция чак-чака + 1 американо", "Чак-чак (мука, мёд) + американо"),
     ("Chak-Chak + Black Coffee", "Combo: chak-chak portion + 1 americano", "Chak-chak (flour, honey) + americano")),
    ("combo", 46000, 25000, True, 4.7, G,
     ("Pechenye to'plami + Milkshake", "Kombinatsiya: pechenye seti + 1 ta milkshake", "Assorti pechenye + shokoladli milkshake"),
     ("Набор печенья + Милкшейк", "Комбо: набор печенья + 1 милкшейк", "Ассорти печенья + шоколадный милкшейк"),
     ("Cookie Set + Milkshake", "Combo: cookie set + 1 milkshake", "Assorted cookies + chocolate milkshake")),
    ("combo", 52000, 28500, True, 4.8, AB,
     ("Rezavorli tort + Smuzi", "Kombinatsiya: tort bo'lagi + 1 ta qulupnay smuzi", "Rezavorli tort bo'lagi + qulupnay smuzi"),
     ("Ягодный торт + Смузи", "Комбо: кусок торта + 1 клубничный смузи", "Кусок ягодного торта + клубничный смузи"),
     ("Berry Cake + Smoothie", "Combo: cake slice + 1 strawberry smoothie", "Berry cake slice + strawberry smoothie")),
]


class Command(BaseCommand):
    help = "CakeBar uchun real rasmli, UZ/RU/EN tarjimali kategoriya va mahsulotlarni yaratadi (mavjudlarini almashtiradi)"

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        cats = {}
        for key, name_uz, name_ru, name_en in CATEGORIES:
            cats[key] = Category.objects.create(name=name_uz, name_ru=name_ru, name_en=name_en)

        for cat_key, price, discount, in_stock, rating, image_url, uz, ru, en in PRODUCTS:
            name, desc, comp = uz
            name_ru, desc_ru, comp_ru = ru
            name_en, desc_en, comp_en = en
            calories, protein_g, fat_g, carbs_g = NUTRITION.get(name, (None, None, None, None))
            qty, qty_ru, qty_en = QUANTITY.get(name, ("", "", ""))
            Product.objects.create(
                name=name, description=desc, composition=comp,
                name_ru=name_ru, description_ru=desc_ru, composition_ru=comp_ru,
                name_en=name_en, description_en=desc_en, composition_en=comp_en,
                quantity=qty, quantity_ru=qty_ru, quantity_en=qty_en,
                category=cats[cat_key], price=price, discount_price=discount,
                in_stock=in_stock, stock_quantity=0 if not in_stock else 25,
                rating=rating, image_url=image_url,
                calories=calories, protein_g=protein_g, fat_g=fat_g, carbs_g=carbs_g,
            )

        self.stdout.write(self.style.SUCCESS(f"{len(cats)} kategoriya va {len(PRODUCTS)} mahsulot yaratildi (UZ/RU/EN)."))
