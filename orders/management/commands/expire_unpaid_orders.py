import time

from django.core.management.base import BaseCommand

from orders.services import expire_unpaid_orders


class Command(BaseCommand):
    help = (
        "Cancels card orders that were never paid and returns their stock. "
        "Run it from cron, or with --loop as a long-running worker process."
    )

    def add_arguments(self, parser):
        parser.add_argument("--loop", action="store_true", help="Keep running, checking every --interval seconds.")
        parser.add_argument("--interval", type=int, default=300)

    def handle(self, *args, **options):
        while True:
            expired = expire_unpaid_orders()
            if expired:
                self.stdout.write(f"Expired unpaid orders: {', '.join(map(str, expired))}")
            if not options["loop"]:
                break
            time.sleep(options["interval"])
