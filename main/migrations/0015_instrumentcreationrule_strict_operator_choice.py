# Generated by Django 4.2 on 2024-01-08 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_instrumentcreationeventlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrumentcreationrule',
            name='strict_operator_choice',
            field=models.CharField(blank=True, choices=[('min', 'min'), ('max', 'max'), ('both', 'both')], max_length=20, null=True),
        ),
    ]