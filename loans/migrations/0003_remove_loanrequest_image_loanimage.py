# Generated by Django 5.1.5 on 2025-04-10 20:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loans', '0002_loanstatushistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loanrequest',
            name='image',
        ),
        migrations.CreateModel(
            name='LoanImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='loan_items_photos/')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='loans.loanrequest')),
            ],
        ),
    ]
