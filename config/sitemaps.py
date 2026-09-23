from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from catalog.models import Category, Product


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(in_stock=True)

    def location(self, obj):
        return reverse("product_detail", args=[obj.id])

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"{reverse('product_list')}?category={obj.id}"


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            "home", "product_list", "about", "locations", "restomarket",
            "production", "events", "contacts", "careers",
        ]

    def location(self, name):
        return reverse(name)
