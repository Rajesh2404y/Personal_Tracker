from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['user', 'created_at'], name='report_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['user', 'date_from', 'date_to'], name='report_user_range_idx'),
        ),
    ]
