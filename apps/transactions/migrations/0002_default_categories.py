from django.db import migrations


DEFAULT_CATEGORIES = [
    ('Food & Dining', 'expense', 'bi-cup-hot', '#f59e0b'),
    ('Housing', 'expense', 'bi-house', '#6366f1'),
    ('Transport', 'expense', 'bi-car-front', '#3b82f6'),
    ('Health', 'expense', 'bi-heart-pulse', '#ef4444'),
    ('Entertainment', 'expense', 'bi-controller', '#8b5cf6'),
    ('Shopping', 'expense', 'bi-cart', '#ec4899'),
    ('Education', 'expense', 'bi-mortarboard', '#14b8a6'),
    ('Utilities', 'expense', 'bi-lightning', '#f97316'),
    ('Travel', 'expense', 'bi-airplane', '#06b6d4'),
    ('Other Expense', 'expense', 'bi-three-dots', '#94a3b8'),
    ('Salary', 'income', 'bi-cash-stack', '#10b981'),
    ('Freelance', 'income', 'bi-laptop', '#10b981'),
    ('Investment', 'income', 'bi-graph-up', '#10b981'),
    ('Business', 'income', 'bi-briefcase', '#10b981'),
    ('Other Income', 'income', 'bi-plus-circle', '#10b981'),
]


def create_default_categories(apps, schema_editor):
    Category = apps.get_model('transactions', 'Category')
    for name, cat_type, icon, color in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name, category_type=cat_type, is_default=True,
            defaults={'icon': icon, 'color': color}
        )


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('transactions', 'Category')
    Category.objects.filter(is_default=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('transactions', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_default_categories, remove_default_categories),
    ]
