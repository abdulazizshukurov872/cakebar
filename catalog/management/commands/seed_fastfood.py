"""Additive, non-destructive: adds the Fastfud category and its products
if they don't already exist, without touching the rest of the catalog
(unlike `seed`, which wipes and recreates everything — not safe to run
again once real customers have favorites/orders on the live site)."""
from django.core.management.base import BaseCommand

from catalog.models import Category, Product

from .seed import CATEGORIES, NUTRITION, PRODUCTS, QUANTITY


class Command(BaseCommand):
    help = "Adds the Fastfud category/products without touching the rest of the catalog."

    def handle(self, *args, **options):
        cat_data = next(c for c in CATEGORIES if c[0] == "fastfud")
        _, name_uz, name_ru, name_en = cat_data
        category, created = Category.objects.get_or_create(
            name=name_uz, defaults={"name_ru": name_ru, "name_en": name_en}
        )
        self.stdout.write(f"Category '{name_uz}' {'created' if created else 'already existed'}.")

        added = 0
        for cat_key, price, discount, in_stock, rating, image_url, uz, ru, en in PRODUCTS:
            if cat_key != "fastfud":
                continue
            name, desc, comp = uz
            name_ru_p, desc_ru, comp_ru = ru
            name_en_p, desc_en, comp_en = en
            if Product.objects.filter(name=name, category=category).exists():
                continue
            calories, protein_g, fat_g, carbs_g = NUTRITION.get(name, (None, None, None, None))
            qty, qty_ru, qty_en = QUANTITY.get(name, ("", "", ""))
            Product.objects.create(
                name=name, description=desc, composition=comp,
                name_ru=name_ru_p, description_ru=desc_ru, composition_ru=comp_ru,
                name_en=name_en_p, description_en=desc_en, composition_en=comp_en,
                quantity=qty, quantity_ru=qty_ru, quantity_en=qty_en,
                category=category, price=price, discount_price=discount,
                in_stock=in_stock, stock_quantity=0 if not in_stock else 25,
                rating=rating, image_url=image_url,
                calories=calories, protein_g=protein_g, fat_g=fat_g, carbs_g=carbs_g,
            )
            added += 1

        self.stdout.write(self.style.SUCCESS(f"Added {added} new fastfud product(s)."))
