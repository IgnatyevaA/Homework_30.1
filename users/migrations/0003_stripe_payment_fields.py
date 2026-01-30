# Generated manually for Stripe payment fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='stripe_session_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Stripe session ID'),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_payment_url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='Stripe payment URL'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[('cash', 'Cash'), ('transfer', 'Transfer'), ('stripe', 'Stripe')],
                max_length=10,
                verbose_name='payment method',
            ),
        ),
    ]
