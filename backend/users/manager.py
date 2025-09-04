from collections import deque
from django.db import connection
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset()

    def get_by_natural_key(self, username):
        username_field = f"{self.model.USERNAME_FIELD}__iexact"
        return self.get(**{username_field: username})

    def _create_user(self, first_name, last_name, phone_number, password, **extra_fields):
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, first_name, last_name, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(first_name, last_name, phone_number, password, **extra_fields)

    def create_superuser(self, first_name, last_name, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(first_name, last_name, phone_number, password, **extra_fields)

    def get_all_descendants(self, user):
        """
        Returns a queryset of all descendants of a given user.
        Uses PostgreSQL CTE if available, otherwise falls back to Python BFS.
        """
        vendor = connection.vendor

        if vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    WITH RECURSIVE descendants AS (
                        SELECT id, created_by_id
                        FROM {self.model._meta.db_table}
                        WHERE created_by_id = %s
                        UNION ALL
                        SELECT u.id, u.created_by_id
                        FROM {self.model._meta.db_table} u
                        INNER JOIN descendants d ON u.created_by_id = d.id
                    )
                    SELECT id FROM descendants;
                """, [user.id])
                ids = [row[0] for row in cursor.fetchall()]
            return self.filter(id__in=ids)

        # fallback: BFS traversal in Python
        visited = set()
        queue = deque(user.created_users.all())
        descendant_ids = []

        while queue:
            child = queue.popleft()
            if child.pk in visited:
                continue
            visited.add(child.pk)
            descendant_ids.append(child.pk)
            queue.extend(child.created_users.all())

        return self.filter(id__in=descendant_ids)

    def get_all_farmers_under(self, user):
        """
        Returns a queryset of all farmers under a given user.
        """
        return self.get_all_descendants(user).filter(user_role="farmer")
