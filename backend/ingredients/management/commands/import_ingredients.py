import csv

from django.core.management.base import BaseCommand
from ingredients.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', type=str, help='The path to the CSV file'
        )

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully imported ingredients')
        )
