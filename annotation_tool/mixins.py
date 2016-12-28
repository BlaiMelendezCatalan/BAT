from django.contrib.auth.mixins import AccessMixin


class SuperuserRequiredMixin(AccessMixin):
    """
    CBV mixin which verifies that for current user is `is_superuser` set to True.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)
