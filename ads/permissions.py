from django.contrib.auth.models import User

from ads.models import Client, User2Client


def check_client_permission(user: User, client: Client, roles: tuple[User2Client.ClientStaffRoles, ...]) -> bool:
    if user.is_superuser:
        return True
    if client.owner == user:
        return True
    return User2Client.objects.filter(client=client, user=user, role__in=roles).exists()
