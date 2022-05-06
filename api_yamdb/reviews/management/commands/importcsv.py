import csv
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Import example data tables in SQLite'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help="file path")

    def handle(self, *args, **kwargs):
        path = kwargs['path']

        if not os.path.exists(path):
            raise CommandError(f'Нет такой директории: {path}')

        model_csv, _ = os.path.splitext(os.path.basename(path))

        try:
            model = apps.get_model('reviews', model_csv.title())
        except LookupError:
            print(f'Модели {model_csv.title()} не существует!')

        model_fields = [f.name for f in model._meta.fields]

        with open(path, 'rt') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            fields_name = next(reader)
            for i, _ in enumerate(fields_name):
                fields_name[i] = fields_name[i].lower()
                fields_name[i] = fields_name[i].replace(' ', '_')
                if not fields_name[i] in model_fields:
                    raise CommandError(
                        f'Поля {fields_name[i]} не существует в модели {model}'
                    )

            for row in reader:
                try:
                    obj = model()
                    for i, field in enumerate(row):
                        setattr(obj, fields_name[i], field)
                    obj.save()
                except Exception as e:
                    raise CommandError(e)

        self.stdout.write(
            self.style.SUCCESS('Loading CSV.')
        )
