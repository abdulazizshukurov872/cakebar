from django.db import migrations


def enable_inscriptions(apps, schema_editor):
    Product = apps.get_model("catalog", "Product")
    Product.objects.filter(category__name="Tortlar").update(allows_inscription=True)


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0009_product_allows_inscription_product_sold_by_weight"),
    ]

    operations = [
        migrations.RunPython(enable_inscriptions, migrations.RunPython.noop),
    ]
