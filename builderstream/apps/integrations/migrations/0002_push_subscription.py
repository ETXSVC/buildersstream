import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0001_initial'),
        ('tenants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSubscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('endpoint', models.TextField()),
                ('p256dh', models.TextField()),
                ('auth', models.TextField()),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_set', to='tenants.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='push_subscriptions', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pushsubscription',
            index=models.Index(fields=['organization', 'user'], name='integ_push_org_user_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='pushsubscription',
            unique_together={('user', 'endpoint')},
        ),
    ]
