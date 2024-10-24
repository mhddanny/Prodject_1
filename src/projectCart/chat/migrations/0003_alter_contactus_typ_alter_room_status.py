# Generated by Django 5.0.6 on 2024-10-09 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='typ',
            field=models.CharField(choices=[('Recommendation', 'Recommendation'), ('Technical issue', 'Technical issue'), ('Money refund', 'Money refund')], max_length=20),
        ),
        migrations.AlterField(
            model_name='room',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('closed', 'Closed'), ('waiting', 'Waiting')], default='waiting', max_length=20),
        ),
    ]
