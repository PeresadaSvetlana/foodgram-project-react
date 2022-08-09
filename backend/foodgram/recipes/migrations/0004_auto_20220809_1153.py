# Generated by Django 3.2.14 on 2022-08-09 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20220801_2003'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name']},
        ),
        migrations.RenameField(
            model_name='ingredient',
            old_name='ingredient',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='number',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='unit_of_measure',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(default=1, max_length=200, verbose_name='Единица измерения'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=256, unique=True, verbose_name='Цвет в HEX'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=256, unique=True, verbose_name='Название'),
        ),
    ]
