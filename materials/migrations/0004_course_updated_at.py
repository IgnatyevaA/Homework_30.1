# Generated manually for Course.updated_at (Celery task: notify only if course not updated 4+ hours)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0003_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='updated at', auto_now=True),
        ),
    ]
