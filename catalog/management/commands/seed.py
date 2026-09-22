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
    ("pechenye", 28000, 24000, True, 4.4, G,
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
    ("konfet", 24000, None, True, 4.3, I_,
     ("Marmelad konfetlar", "Rangli, 250gr", "Shakar, pektin, meva sharbati, limon kislotasi, tabiiy bo'yoqlar"),
     ("Мармеладные конфеты", "Разноцветные, 250г", "Сахар, пектин, фруктовый сок, лимонная кислота, натуральные красители"),
     ("Marmalade Candy", "Colorful, 250g", "Sugar, pectin, fruit juice, citric acid, natural colorings")),

    ("makaron", 38000, None, True, 4.8, H,
     ("Rangli makaron to'plami", "12 dona, aralash ta'm", "Bodom uni, quandagi oqsil, shakar, pishirish kukuni, turli ta'mli kremlar"),
     ("Набор цветных макарун", "12 шт., ассорти вкусов", "Миндальная мука, яичный белок, сахар, разрыхлитель, кремы разных вкусов"),
     ("Colorful Macaron Set", "12 pcs, assorted flavors", "Almond flour, egg white, sugar, baking powder, assorted flavored fillings")),
    ("makaron", 22000, None, True, 4.6, H,
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
    ("muzqaymoq", 30000, None, True, 4.4, K,
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

    ("combo", 30000, 16500, True, 4.8, CB1,
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
    ("combo", 40000, 22000, True, 4.6, E,
     ("2 ta Donut + Amerikano", "Kombinatsiya: 2 ta donut + 1 ta amerikano", "Klassik va shokoladli donut + amerikano"),
     ("2 Пончика + Американо", "Комбо: 2 пончика + 1 американо", "Классический и шоколадный пончик + американо"),
     ("2 Donuts + Americano", "Combo: 2 donuts + 1 americano", "Classic and chocolate donut + americano")),
    ("combo", 48000, 26000, True, 4.8, H,
     ("Makaron seti + Espresso", "Kombinatsiya: 6 dona makaron + 1 ta espresso", "Aralash ta'mli makaronlar + espresso"),
     ("Набор макарун + Эспрессо", "Комбо: 6 макарун + 1 эспрессо", "Ассорти макарун + эспрессо"),
     ("Macaron Set + Espresso", "Combo: 6 macarons + 1 espresso", "Assorted macarons + espresso")),
    ("combo", 34000, 18500, True, 4.6, P,
     ("Ezoklair + Kapuchino", "Kombinatsiya: 1 ta ezoklair + 1 ta kapuchino", "Ezoklair (zavarnoy xamir, vanil krem) + kapuchino"),
     ("Эклер + Капучино", "Комбо: 1 эклер + 1 капучино", "Эклер (заварное тесто, ванильный крем) + капучино"),
     ("Eclair + Cappuccino", "Combo: 1 eclair + 1 cappuccino", "Eclair (choux pastry, vanilla cream) + cappuccino")),
    ("combo", 38000, 21000, True, 4.5, W,
     ("Shokoladli muffin + Limonad", "Kombinatsiya: 1 ta muffin + 1 ta limonad", "Shokoladli muffin + uy usulida limonad"),
     ("Шоколадный маффин + Лимонад", "Комбо: 1 маффин + 1 лимонад", "Шоколадный маффин + домашний лимонад"),
     ("Chocolate Muffin + Lemonade", "Combo: 1 muffin + 1 lemonade", "Chocolate muffin + homemade lemonade")),
    ("combo", 42000, 23000, True, 4.6, Y,
     ("Chak-chak + Qora kofe", "Kombinatsiya: chak-chak porsiyasi + 1 ta amerikano", "Chak-chak (un, asal) + amerikano"),
     ("Чак-чак + Чёрный кофе", "Комбо: порция чак-чака + 1 американо", "Чак-чак (мука, мёд) + американо"),
     ("Chak-Chak + Black Coffee", "Combo: chak-chak portion + 1 americano", "Chak-chak (flour, honey) + americano")),
    ("combo", 46000, 25000, True, 4.7, G,
     ("Pechenye to'plami + Milkshake", "Kombinatsiya: pechenye seti + 1 ta milkshake", "Assorti pechenye + shokoladli milkshake"),
     ("Набор печенья + Милкшейк", "Комбо: набор печенья + 1 милкшейк", "Ассорти печенья + шоколадный милкшейк"),
     ("Cookie Set + Milkshake", "Combo: cookie set + 1 milkshake", "Assorted cookies + chocolate milkshake")),
    ("combo", 52000, 28500, True, 4.8, B,
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
            Product.objects.create(
                name=name, description=desc, composition=comp,
                name_ru=name_ru, description_ru=desc_ru, composition_ru=comp_ru,
                name_en=name_en, description_en=desc_en, composition_en=comp_en,
                category=cats[cat_key], price=price, discount_price=discount,
                in_stock=in_stock, rating=rating, image_url=image_url,
            )

        self.stdout.write(self.style.SUCCESS(f"{len(cats)} kategoriya va {len(PRODUCTS)} mahsulot yaratildi (UZ/RU/EN)."))
