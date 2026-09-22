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
CB2 = IMG.format("1495474472287-4d71bcdd2085")  # flatlay combo
CB3 = IMG.format("1517686469429-8bdb88b9f907")  # flatlay combo

# extra unique images (reduce duplicates + new products)
NI1 = IMG.format("1509365465985-25d11c17e812")   # cinnamon rolls
NI2 = IMG.format("1587314168485-3236d6710814")   # cheesecake
NI3 = IMG.format("1533134242443-d4fd215305ad")   # brownies
NI4 = IMG.format("1568051243851-f9b136146e97")   # croissant
NI5 = IMG.format("1587985064135-0366536eab42")   # red velvet cupcake
NI6 = IMG.format("1541696490-8744a5dc0228")      # waffles
NI7 = IMG.format("1605270012917-bf157c5a9541")   # pralines box
NI8 = IMG.format("1490474418585-ba9bad8fd0ea")   # baklava
NI9 = IMG.format("1608219992759-8d74ed8d76eb")   # iced coffee
NI10 = IMG.format("1558326567-98ae2405596b")     # hot chocolate
NI11 = IMG.format("1519676867240-f03562e64548")  # fruit tart
NI12 = IMG.format("1587574293340-e0011c4e8ecf")  # cannoli
NI13 = IMG.format("1516684732162-798a0062be99")  # cookies plate
NI14 = IMG.format("1607478900766-efe13248b125")  # muffins tray
NI15 = IMG.format("1522336284037-91f7da073525")  # macarons close-up
NI16 = IMG.format("1481391319762-47dff72954d9")  # candy assorted
NI17 = IMG.format("1495147466023-ac5c588e2e94")  # sorbet scoops
NI18 = IMG.format("1483695028939-5bb13f8648b0")  # donuts stack
NI19 = IMG.format("1626094309830-abbb0c99da4a")  # pink donut alt

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
    ("combo", "Haftalik chegirmalar", "Скидки недели", "Weekly Deals"),
]

# Each entry: cat_key, price, discount, in_stock, rating, image,
#   (name_uz, desc_uz, comp_uz), (name_ru, desc_ru, comp_ru), (name_en, desc_en, comp_en)
PRODUCTS = [
    ("tort", 250000, 210000, True, 4.8, A,
     ("Shokoladli tort", "Uch qavatli, krem bilan", "Bug'doy uni, shakar, tuxum, kakao kukuni, sariyog', sut, ishlov berilgan shokolad, pishirish kukuni"),
     ("Шоколадный торт", "Трёхслойный, с кремом", "Пшеничная мука, сахар, яйца, какао-порошок, сливочное масло, молоко, шоколад, разрыхлитель"),
     ("Chocolate Cake", "Three layers, with cream", "Wheat flour, sugar, eggs, cocoa powder, butter, milk, chocolate, baking powder")),
    ("tort", 280000, None, True, 4.7, B,
     ("Rezavorli tort", "Yovvoyi rezavorlar bilan bezatilgan", "Bug'doy uni, shakar, tuxum, sariyog', qaymoq krem, mavsumiy rezavorlar (qulupnay, malina, ko'k smorodina)"),
     ("Ягодный торт", "Украшен лесными ягодами", "Пшеничная мука, сахар, яйца, сливочное масло, сливочный крем, сезонные ягоды (клубника, малина, смородина)"),
     ("Berry Cake", "Decorated with wild berries", "Wheat flour, sugar, eggs, butter, cream, seasonal berries (strawberry, raspberry, blackcurrant)")),
    ("tort", 450000, None, True, 4.9, C,
     ("Nikoh torti", "Oq krem, ko'p qavatli", "Bug'doy uni, shakar, tuxum, sariyog', vanil ekstrakti, oq shokolad, mastika bezak"),
     ("Свадебный торт", "Белый крем, многоярусный", "Пшеничная мука, сахар, яйца, сливочное масло, экстракт ванили, белый шоколад, мастика"),
     ("Wedding Cake", "White cream, multi-tier", "Wheat flour, sugar, eggs, butter, vanilla extract, white chocolate, fondant decoration")),

    ("pirojnoye", 18000, None, True, 4.6, N,
     ("Napoleon pirojnoye", "Qatlamli xamir, vanil krem", "Qatlamli xamir (un, sariyog', tuxum), vanil krem (sut, shakar, tuxum sarig'i, kraxmal)"),
     ("Наполеон", "Слоёное тесто, ванильный крем", "Слоёное тесто (мука, масло, яйца), ванильный крем (молоко, сахар, желток, крахмал)"),
     ("Napoleon Pastry", "Puff pastry, vanilla cream", "Puff pastry (flour, butter, eggs), vanilla cream (milk, sugar, egg yolk, starch)")),
    ("pirojnoye", 32000, 27000, True, 4.8, O,
     ("Tiramisu", "Kofe va mascarpone bilan", "Mascarpone pishloq, savoyardi pechenye, espresso kofe, kakao kukuni, tuxum, shakar"),
     ("Тирамису", "С кофе и маскарпоне", "Сыр маскарпоне, печенье савоярди, кофе эспрессо, какао-порошок, яйца, сахар"),
     ("Tiramisu", "With coffee and mascarpone", "Mascarpone cheese, savoiardi biscuits, espresso coffee, cocoa powder, eggs, sugar")),
    ("pirojnoye", 16000, None, True, 4.5, P,
     ("Ezoklair", "Shokolad glazur bilan", "Zavarnoy xamir (un, sariyog', tuxum), vanil krem, shokolad glazur"),
     ("Эклер", "С шоколадной глазурью", "Заварное тесто (мука, масло, яйца), ванильный крем, шоколадная глазурь"),
     ("Eclair", "With chocolate glaze", "Choux pastry (flour, butter, eggs), vanilla cream, chocolate glaze")),

    ("donut", 15000, None, True, 4.4, E,
     ("Klassik donut", "Shakar glazur bilan", "Bug'doy uni, shakar, xamirturush, sut, tuxum, o'simlik moyi, shakar glazur"),
     ("Классический пончик", "С сахарной глазурью", "Пшеничная мука, сахар, дрожжи, молоко, яйца, растительное масло, сахарная глазурь"),
     ("Classic Donut", "With sugar glaze", "Wheat flour, sugar, yeast, milk, eggs, vegetable oil, sugar glaze")),
    ("donut", 17000, 14000, True, 4.6, F,
     ("Shokoladli donut", "Shokolad glazur, sprinkle", "Bug'doy uni, shakar, xamirturush, sut, tuxum, shokolad glazur, rangli sprinkle"),
     ("Шоколадный пончик", "Шоколадная глазурь, посыпка", "Пшеничная мука, сахар, дрожжи, молоко, яйца, шоколадная глазурь, цветная посыпка"),
     ("Chocolate Donut", "Chocolate glaze, sprinkles", "Wheat flour, sugar, yeast, milk, eggs, chocolate glaze, colorful sprinkles")),
    ("donut", 17000, None, True, 4.5, Q,
     ("Pushti glazurli donut", "Meva ta'mi glazur", "Bug'doy uni, shakar, xamirturush, sut, tuxum, meva ta'mli glazur (qulupnay)"),
     ("Пончик с розовой глазурью", "Фруктовая глазурь", "Пшеничная мука, сахар, дрожжи, молоко, яйца, фруктовая глазурь (клубника)"),
     ("Pink Glazed Donut", "Fruit-flavored glaze", "Wheat flour, sugar, yeast, milk, eggs, fruit glaze (strawberry)")),

    ("pechenye", 32000, None, True, 4.6, G,
     ("Choco-chip pechenye", "12 dona quti", "Bug'doy uni, sariyog', jigarrang shakar, tuxum, shokolad bo'lakchalari, vanil"),
     ("Печенье с шоколадной крошкой", "Упаковка 12 шт.", "Пшеничная мука, сливочное масло, коричневый сахар, яйца, кусочки шоколада, ваниль"),
     ("Choco-Chip Cookies", "Box of 12", "Wheat flour, butter, brown sugar, eggs, chocolate chips, vanilla")),
    ("pechenye", 28000, 24000, True, 4.4, NI13,
     ("Oatmeal pechenye", "Yormali, asal bilan", "Suli yormasi, bug'doy uni, asal, sariyog', mayiz, tarkan"),
     ("Овсяное печенье", "С овсянкой и мёдом", "Овсяные хлопья, пшеничная мука, мёд, сливочное масло, изюм, корица"),
     ("Oatmeal Cookies", "With oats and honey", "Oat flakes, wheat flour, honey, butter, raisins, cinnamon")),
    ("pechenye", 35000, None, True, 4.5, M,
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

    ("konfet", 25000, None, True, 4.3, I_,
     ("Jele konfetlar", "Meva ta'mi, 300gr", "Shakar, glyukoza siropi, jelatin, meva sharbati kontsentrati, limon kislotasi"),
     ("Желейные конфеты", "Фруктовый вкус, 300г", "Сахар, глюкозный сироп, желатин, концентрат фруктового сока, лимонная кислота"),
     ("Jelly Candy", "Fruit flavor, 300g", "Sugar, glucose syrup, gelatin, fruit juice concentrate, citric acid")),
    ("konfet", 22000, None, False, 4.2, AA,
     ("Karamel konfet", "Yumshoq karamel, 250gr", "Shakar, glyukoza siropi, sariyog', qaymoq, vanil"),
     ("Карамельные конфеты", "Мягкая карамель, 250г", "Сахар, глюкозный сироп, сливочное масло, сливки, ваниль"),
     ("Caramel Candy", "Soft caramel, 250g", "Sugar, glucose syrup, butter, cream, vanilla")),
    ("konfet", 24000, None, True, 4.3, NI16,
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
    ("makaron", 22000, 19000, True, 4.7, H,
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
    ("muzqaymoq", 30000, None, True, 4.4, NI17,
     ("Rezavorli sorbet", "500ml, sut mahsulotsiz", "Meva pyuresi (rezavorlar), shakar, suv, limon sharbati"),
     ("Ягодный сорбет", "500мл, без молочных продуктов", "Фруктовое пюре (ягоды), сахар, вода, лимонный сок"),
     ("Berry Sorbet", "500ml, dairy-free", "Fruit puree (berries), sugar, water, lemon juice")),

    ("milliy", 32000, None, True, 4.6, T,
     ("Halva", "An'anaviy, yong'oqli, 400gr", "Kunjut yog'i, shakar siropi, sovun ildizi ekstrakti, yong'oq"),
     ("Халва", "Традиционная, с орехами, 400г", "Кунжутное масло, сахарный сироп, экстракт мыльного корня, орехи"),
     ("Halva", "Traditional, with nuts, 400g", "Sesame oil, sugar syrup, soapwort root extract, nuts")),
    ("milliy", 20000, None, True, 4.4, U,
     ("Parvarda", "Qand asosida tayyorlangan, 300gr", "Shakar, suv, limon kislotasi, vanil"),
     ("Парварда", "На основе сахара, 300г", "Сахар, вода, лимонная кислота, ваниль"),
     ("Parvarda", "Sugar-based, 300g", "Sugar, water, citric acid, vanilla")),
    ("milliy", 26000, None, True, 4.5, Y,
     ("Chak-chak", "Asal bilan, 400gr", "Un, tuxum, asal, o'simlik moyi (qovurish uchun)"),
     ("Чак-чак", "С мёдом, 400г", "Мука, яйца, мёд, растительное масло (для жарки)"),
     ("Chak-Chak", "With honey, 400g", "Flour, eggs, honey, vegetable oil (for frying)")),

    ("keks", 24000, None, True, 4.5, D,
     ("Vanil keksi", "Mini keks, 6 dona", "Bug'doy uni, sariyog', shakar, tuxum, vanil, pishirish kukuni"),
     ("Ванильный кекс", "Мини-кекс, 6 шт.", "Пшеничная мука, сливочное масло, сахар, яйца, ваниль, разрыхлитель"),
     ("Vanilla Cupcakes", "Mini, 6 pcs", "Wheat flour, butter, sugar, eggs, vanilla, baking powder")),
    ("keks", 26000, 22000, True, 4.6, W,
     ("Shokoladli muffin", "6 dona", "Bug'doy uni, kakao, shakar, tuxum, sariyog', shokolad bo'lakchalari"),
     ("Шоколадный маффин", "6 шт.", "Пшеничная мука, какао, сахар, яйца, сливочное масло, кусочки шоколада"),
     ("Chocolate Muffins", "6 pcs", "Wheat flour, cocoa, sugar, eggs, butter, chocolate chips")),
    ("keks", 27000, None, True, 4.5, AB,
     ("Limonli keks", "Limon glazur bilan", "Bug'doy uni, sariyog', shakar, tuxum, limon qobig'i va sharbati, glazur"),
     ("Лимонный кекс", "С лимонной глазурью", "Пшеничная мука, сливочное масло, сахар, яйца, цедра и сок лимона, глазурь"),
     ("Lemon Cake", "With lemon glaze", "Wheat flour, butter, sugar, eggs, lemon zest and juice, glaze")),

    ("ichimlik", 18000, None, True, 4.6, DR2,
     ("Apelsin sharbati", "Yangi siqilgan, 500ml", "100% apelsin sharbati, konservantsiz"),
     ("Апельсиновый сок", "Свежевыжатый, 500мл", "100% апельсиновый сок, без консервантов"),
     ("Orange Juice", "Freshly squeezed, 500ml", "100% orange juice, no preservatives")),
    ("ichimlik", 20000, None, True, 4.5, DR3,
     ("Qulupnay smuzi", "Tabiiy, 400ml", "Qulupnay, banan, tabiiy yogurt, asal"),
     ("Клубничный смузи", "Натуральный, 400мл", "Клубника, банан, натуральный йогурт, мёд"),
     ("Strawberry Smoothie", "Natural, 400ml", "Strawberry, banana, natural yogurt, honey")),
    ("ichimlik", 15000, None, True, 4.4, DR1,
     ("Limonad", "Uy usulida, 500ml", "Suv, limon sharbati, shakar, yalpiz"),
     ("Лимонад", "Домашний, 500мл", "Вода, лимонный сок, сахар, мята"),
     ("Lemonade", "Homemade, 500ml", "Water, lemon juice, sugar, mint")),
    ("ichimlik", 22000, 18000, True, 4.7, DR7,
     ("Shokoladli milkshake", "450ml", "Sut, muzqaymoq, shokolad siropi, qaymoq"),
     ("Шоколадный милкшейк", "450мл", "Молоко, мороженое, шоколадный сироп, сливки"),
     ("Chocolate Milkshake", "450ml", "Milk, ice cream, chocolate syrup, cream")),

    ("qahva", 12000, None, True, 4.6, CF1,
     ("Espresso", "30ml, klassik", "100% arabika kofe donlari"),
     ("Эспрессо", "30мл, классика", "100% зёрна арабики"),
     ("Espresso", "30ml, classic", "100% arabica coffee beans")),
    ("qahva", 18000, None, True, 4.7, CF2,
     ("Kapuchino", "200ml, sut ko'pigi bilan", "Espresso, bug'langan sut, sut ko'pigi"),
     ("Капучино", "200мл, с молочной пенкой", "Эспрессо, взбитое молоко, молочная пенка"),
     ("Cappuccino", "200ml, with milk foam", "Espresso, steamed milk, milk foam")),
    ("qahva", 20000, None, True, 4.6, CF3,
     ("Latte", "250ml, yumshoq ta'm", "Espresso, ko'p sut, ozgina sut ko'pigi"),
     ("Латте", "250мл, мягкий вкус", "Эспрессо, много молока, немного молочной пенки"),
     ("Latte", "250ml, smooth taste", "Espresso, lots of milk, a little milk foam")),
    ("qahva", 14000, None, True, 4.4, CF4,
     ("Amerikano", "220ml", "Espresso, issiq suv"),
     ("Американо", "220мл", "Эспрессо, горячая вода"),
     ("Americano", "220ml", "Espresso, hot water")),

    ("combo", 30000, 16500, True, 4.8, NI14,
     ("Napoleon + Espresso", "Kombinatsiya: 1 ta Napoleon pirojnoye + 1 ta espresso", "Napoleon pirojnoye (qatlamli xamir, vanil krem) + espresso (arabika)"),
     ("Наполеон + Эспрессо", "Комбо: 1 Наполеон + 1 эспрессо", "Наполеон (слоёное тесто, ванильный крем) + эспрессо (арабика)"),
     ("Napoleon + Espresso", "Combo: 1 Napoleon pastry + 1 espresso", "Napoleon (puff pastry, vanilla cream) + espresso (arabica)")),
    ("combo", 50000, 27500, True, 4.9, CB2,
     ("Tiramisu + Kapuchino", "Kombinatsiya: 1 ta tiramisu + 1 ta kapuchino", "Tiramisu (mascarpone, kofe, kakao) + kapuchino (espresso, sut ko'pigi)"),
     ("Тирамису + Капучино", "Комбо: 1 тирамису + 1 капучино", "Тирамису (маскарпоне, кофе, какао) + капучино (эспрессо, молочная пенка)"),
     ("Tiramisu + Cappuccino", "Combo: 1 tiramisu + 1 cappuccino", "Tiramisu (mascarpone, coffee, cocoa) + cappuccino (espresso, milk foam)")),
    ("combo", 45000, 24500, True, 4.7, CB3,
     ("Shokoladli tort + Latte", "Kombinatsiya: tort bo'lagi + 1 ta latte", "Shokoladli tort bo'lagi + latte (espresso, sut)"),
     ("Шоколадный торт + Латте", "Комбо: кусок торта + 1 латте", "Кусок шоколадного торта + латте (эспрессо, молоко)"),
     ("Chocolate Cake + Latte", "Combo: cake slice + 1 latte", "Chocolate cake slice + latte (espresso, milk)")),
    ("combo", 40000, 22000, True, 4.6, NI18,
     ("2 ta Donut + Amerikano", "Kombinatsiya: 2 ta donut + 1 ta amerikano", "Klassik va shokoladli donut + amerikano"),
     ("2 Пончика + Американо", "Комбо: 2 пончика + 1 американо", "Классический и шоколадный пончик + американо"),
     ("2 Donuts + Americano", "Combo: 2 donuts + 1 americano", "Classic and chocolate donut + americano")),
    ("combo", 48000, 26000, True, 4.8, H,
     ("Makaron seti + Espresso", "Kombinatsiya: 6 dona makaron + 1 ta espresso", "Aralash ta'mli makaronlar + espresso"),
     ("Набор макарун + Эспрессо", "Комбо: 6 макарун + 1 эспрессо", "Ассорти макарун + эспрессо"),
     ("Macaron Set + Espresso", "Combo: 6 macarons + 1 espresso", "Assorted macarons + espresso")),
    ("combo", 34000, 18500, True, 4.6, CF2,
     ("Ezoklair + Kapuchino", "Kombinatsiya: 1 ta ezoklair + 1 ta kapuchino", "Ezoklair (zavarnoy xamir, vanil krem) + kapuchino"),
     ("Эклер + Капучино", "Комбо: 1 эклер + 1 капучино", "Эклер (заварное тесто, ванильный крем) + капучино"),
     ("Eclair + Cappuccino", "Combo: 1 eclair + 1 cappuccino", "Eclair (choux pastry, vanilla cream) + cappuccino")),
    ("combo", 38000, 21000, True, 4.5, NI19,
     ("Shokoladli muffin + Limonad", "Kombinatsiya: 1 ta muffin + 1 ta limonad", "Shokoladli muffin + uy usulida limonad"),
     ("Шоколадный маффин + Лимонад", "Комбо: 1 маффин + 1 лимонад", "Шоколадный маффин + домашний лимонад"),
     ("Chocolate Muffin + Lemonade", "Combo: 1 muffin + 1 lemonade", "Chocolate muffin + homemade lemonade")),
    ("combo", 42000, 23000, True, 4.6, CF4,
     ("Chak-chak + Qora kofe", "Kombinatsiya: chak-chak porsiyasi + 1 ta amerikano", "Chak-chak (un, asal) + amerikano"),
     ("Чак-чак + Чёрный кофе", "Комбо: порция чак-чака + 1 американо", "Чак-чак (мука, мёд) + американо"),
     ("Chak-Chak + Black Coffee", "Combo: chak-chak portion + 1 americano", "Chak-chak (flour, honey) + americano")),
    ("combo", 46000, 25000, True, 4.7, DR7,
     ("Pechenye to'plami + Milkshake", "Kombinatsiya: pechenye seti + 1 ta milkshake", "Assorti pechenye + shokoladli milkshake"),
     ("Набор печенья + Милкшейк", "Комбо: набор печенья + 1 милкшейк", "Ассорти печенья + шоколадный милкшейк"),
     ("Cookie Set + Milkshake", "Combo: cookie set + 1 milkshake", "Assorted cookies + chocolate milkshake")),
    ("combo", 52000, 28500, True, 4.8, DR3,
     ("Rezavorli tort + Smuzi", "Kombinatsiya: tort bo'lagi + 1 ta qulupnay smuzi", "Rezavorli tort bo'lagi + qulupnay smuzi"),
     ("Ягодный торт + Смузи", "Комбо: кусок торта + 1 клубничный смузи", "Кусок ягодного торта + клубничный смузи"),
     ("Berry Cake + Smoothie", "Combo: cake slice + 1 strawberry smoothie", "Berry cake slice + strawberry smoothie")),

    ("tort", 65000, 55000, True, 4.8, NI2,
     ("Cheesecake", "Nyu-York uslubida, tvorojli krem", "Krem pishloq, shakar, tuxum, gallet pechenye, sariyog'"),
     ("Чизкейк", "Нью-Йоркский стиль, творожный крем", "Сливочный сыр, сахар, яйца, печенье, сливочное масло"),
     ("Cheesecake", "New York style, cream cheese filling", "Cream cheese, sugar, eggs, biscuit crust, butter")),
    ("tort", 28000, None, True, 4.6, NI11,
     ("Mevali tart", "Mavsumiy mevalar bilan, individual", "Un, sariyog', qaymoq krem, mavsumiy mevalar"),
     ("Фруктовый тарт", "С сезонными фруктами, порционный", "Мука, сливочное масло, сливочный крем, сезонные фрукты"),
     ("Fruit Tart", "With seasonal fruit, individual size", "Flour, butter, cream filling, seasonal fruit")),

    ("pirojnoye", 16000, None, True, 4.6, NI1,
     ("Dolchinli rulet", "Yumshoq xamir, dolchinli krem bilan", "Bug'doy uni, sariyog', shakar, dolchin, tuxum, krem pishloq glazur"),
     ("Булочка с корицей", "Мягкое тесто с корично-масляной начинкой", "Пшеничная мука, сливочное масло, сахар, корица, яйца, глазурь из сливочного сыра"),
     ("Cinnamon Roll", "Soft dough with cinnamon-butter filling", "Wheat flour, butter, sugar, cinnamon, eggs, cream cheese glaze")),
    ("pirojnoye", 14000, None, True, 4.5, NI4,
     ("Kruassan", "Frantsuz uslubida, varaqlangan", "Bug'doy uni, sariyog', xamirturush, tuz, shakar"),
     ("Круассан", "Французский, слоёный", "Пшеничная мука, сливочное масло, дрожжи, соль, сахар"),
     ("Croissant", "French-style, flaky layers", "Wheat flour, butter, yeast, salt, sugar")),
    ("pirojnoye", 24000, None, True, 4.6, NI6,
     ("Belgiya vaflisi", "Asal va rezavorlar bilan", "Un, tuxum, sut, sariyog', shakar, asal, rezavorlar"),
     ("Бельгийская вафля", "С мёдом и ягодами", "Мука, яйца, молоко, сливочное масло, сахар, мёд, ягоды"),
     ("Belgian Waffle", "With honey and berries", "Flour, eggs, milk, butter, sugar, honey, berries")),
    ("pirojnoye", 21000, None, True, 4.7, NI12,
     ("Cannoli", "Sitsiliya uslubida, rikotta krem", "Xamir naycha, rikotta pishloq, shakar, shokolad bo'lakchalari"),
     ("Канноли", "Сицилийский стиль, крем рикотта", "Хрустящая трубочка, сыр рикотта, сахар, кусочки шоколада"),
     ("Cannoli", "Sicilian style, ricotta cream", "Crispy pastry tube, ricotta cheese, sugar, chocolate chips")),

    ("shokolad", 20000, None, True, 4.7, NI3,
     ("Shokoladli brauni", "Zich va yumshoq, yong'oqli", "Qora shokolad, sariyog', shakar, tuxum, un, yong'oq"),
     ("Шоколадный брауни", "Плотный и мягкий, с орехами", "Тёмный шоколад, сливочное масло, сахар, яйца, мука, орехи"),
     ("Chocolate Brownie", "Dense and fudgy, with walnuts", "Dark chocolate, butter, sugar, eggs, flour, walnuts")),
    ("shokolad", 48000, 42000, True, 4.8, NI7,
     ("Praline to'plami", "Yong'oqli praline konfetlar, 200gr", "Shokolad, findiq, shakar, sariyog'"),
     ("Набор пралине", "Ореховые конфеты пралине, 200г", "Шоколад, фундук, сахар, сливочное масло"),
     ("Praline Box", "Hazelnut praline chocolates, 200g", "Chocolate, hazelnuts, sugar, butter")),

    ("milliy", 34000, None, True, 4.7, NI8,
     ("Baklava", "Yong'oqli, asal siropida", "Yupqa xamir varaqlari, yong'oq, asal, sariyog'"),
     ("Пахлава", "Ореховая, в медовом сиропе", "Тонкие слои теста, орехи, мёд, сливочное масло"),
     ("Baklava", "With nuts, in honey syrup", "Thin pastry layers, nuts, honey, butter")),

    ("keks", 23000, None, True, 4.6, NI5,
     ("Red Velvet keks", "Qizil pishiriq, cream cheese krem", "Bug'doy uni, kakao, qizil bo'yoq, tuxum, sariyog', krem pishloq"),
     ("Кекс Red Velvet", "Красный бисквит, крем чиз", "Пшеничная мука, какао, пищевой краситель, яйца, масло, сливочный сыр"),
     ("Red Velvet Cupcake", "Red sponge, cream cheese frosting", "Wheat flour, cocoa, food coloring, eggs, butter, cream cheese")),

    ("ichimlik", 19000, None, True, 4.6, NI10,
     ("Issiq shokolad", "300ml, qaymoq bilan", "Sut, qora shokolad, shakar, qaymoq"),
     ("Горячий шоколад", "300мл, со сливками", "Молоко, тёмный шоколад, сахар, сливки"),
     ("Hot Chocolate", "300ml, with whipped cream", "Milk, dark chocolate, sugar, cream")),

    ("qahva", 22000, None, True, 4.6, NI9,
     ("Muzli latte", "300ml, sovuq ichimlik", "Espresso, sovuq sut, muz"),
     ("Айс латте", "300мл, холодный напиток", "Эспрессо, холодное молоко, лёд"),
     ("Iced Latte", "300ml, cold drink", "Espresso, cold milk, ice")),
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
            Product.objects.create(
                name=name, description=desc, composition=comp,
                name_ru=name_ru, description_ru=desc_ru, composition_ru=comp_ru,
                name_en=name_en, description_en=desc_en, composition_en=comp_en,
                category=cats[cat_key], price=price, discount_price=discount,
                in_stock=in_stock, stock_quantity=0 if not in_stock else 25,
                rating=rating, image_url=image_url,
                calories=calories, protein_g=protein_g, fat_g=fat_g, carbs_g=carbs_g,
            )

        self.stdout.write(self.style.SUCCESS(f"{len(cats)} kategoriya va {len(PRODUCTS)} mahsulot yaratildi (UZ/RU/EN)."))
