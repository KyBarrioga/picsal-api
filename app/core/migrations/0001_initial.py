from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("display_name", models.CharField(blank=True, default="", max_length=255)),
                ("avatar_path", models.CharField(blank=True, default="", max_length=512)),
                (
                    "role",
                    models.CharField(
                        choices=[("user", "User"), ("admin", "Admin"), ("superuser", "Superuser")],
                        default="user",
                        max_length=20,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("last_login_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "user_profiles",
                "ordering": ["email"],
            },
        ),
    ]
