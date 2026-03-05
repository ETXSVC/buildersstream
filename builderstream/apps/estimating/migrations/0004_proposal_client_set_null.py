from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0001_initial"),
        ("estimating", "0003_add_currency_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="proposal",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="proposals",
                to="crm.contact",
            ),
        ),
    ]
