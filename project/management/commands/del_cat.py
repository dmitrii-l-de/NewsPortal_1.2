from django.core.management.base import BaseCommand, CommandError
from project.models import Post, Category, PostCategory


class Command(BaseCommand):
    help = 'Подсказка вашей команды'
    requires_migrations_checks = True  # напоминать ли о миграциях. Если true —
    # то будет напоминание о том, что не сделаны все миграции (если такие есть)

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        answer = input(f'Вы правда хотите удалить все статьи в категории {options["category"]}? yes/no: ')

        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Отменено'))

        try:
            cat_name = Category.objects.get(category_name=options['category'])
            category_id = Category.objects.get(category_name=options['category']).id
            posts_to_delete = Post.objects.filter(category=category_id)

            posts_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Succesfully deleted all news from category {cat_name}'))  # в случае неправильного подтверждения говорим, что в доступе отказано
        except Post.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Could not find category {cat_name}'))
