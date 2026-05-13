from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('transactions', '0002_default_categories'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'transaction_type', 'date'], name='txn_user_type_date_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'category', 'date'], name='txn_user_cat_date_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'date', 'created_at'], name='txn_user_date_created_idx'),
        ),
    ]
