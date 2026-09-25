"""Additive, non-destructive: creates/updates the Fastfud category and its
products from seed.py's data, without touching the rest of the catalog or
any other product's stock (unlike `seed`, which wipes and recreates
everything — not safe to run again once real customers have
favorites/orders on the live site).

Text fields (name/description/composition/price/nutrition/quantity) are
kept in sync with seed.py on every run — so a typo fix here reaches
production on the next deploy without a manual DB edit. Stock fields
(in_stock/stock_quantity) are only set when a product is first created,
so this never overwrites stock an admin has since adjusted by hand.
"""
from django.core.management.base import BaseCommand

from catalog.models import Category, Product

from .seed import CATEGORIES, NUTRITION, PRODUCTS, QUANTITY


class Command(BaseCommand):
    help = "Creates/updates the Fastfud category/products without touching the rest of the catalog."

    def handle(self, *args, **options):
        cat_data = next(c for c in CATEGORIES if c[0] == "fastfud")
        _, name_uz, name_ru, name_en = cat_data
        category, created = Category.objects.get_or_create(
            name=name_uz, defaults={"name_ru": name_ru, "name_en": name_en}
        )
        self.stdout.write(f"Category '{name_uz}' {'created' if created else 'already existed'}.")

        created_count = updated_count = 0
        for cat_key, price, discount, in_stock, rating, image_url, uz, ru, en in PRODUCTS:
            if cat_key != "fastfud":
                continue
            name, desc, comp = uz
            name_ru_p, desc_ru, comp_ru = ru
            name_en_p, desc_en, comp_en = en
            calories, protein_g, fat_g, carbs_g = NUTRITION.get(name, (None, None, None, None))
            qty, qty_ru, qty_en = QUANTITY.get(name, ("", "", ""))
            product, was_created = Product.objects.update_or_create(
                name=name, category=category,
                defaults=dict(
                    description=desc, composition=comp,
                    name_ru=name_ru_p, description_ru=desc_ru, composition_ru=comp_ru,
                    name_en=name_en_p, description_en=desc_en, composition_en=comp_en,
                    quantity=qty, quantity_ru=qty_ru, quantity_en=qty_en,
                    price=price, discount_price=discount, image_url=image_url,
                    rating=rating,
                    calories=calories, protein_g=protein_g, fat_g=fat_g, carbs_g=carbs_g,
                ),
            )
            if was_created:
                product.in_stock = in_stock
                product.stock_quantity = 0 if not in_stock else 25
                product.save(update_fields=["in_stock", "stock_quantity"])
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Fastfud: {created_count} created, {updated_count} updated (text/price kept in sync)."
        ))
