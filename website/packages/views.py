from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.views.generic import CreateView, DetailView, ListView, UpdateView,\
        FormView
from django.views.generic.detail import SingleObjectMixin

from .forms import PackageCreateEditForm, PackageFlagForm
from .models import Package


class PackageEditMixin(object):
    """Users may only edit and delete packages they created."""

    def get_object(self, queryset=None):
        obj = super(PackageEditMixin, self).get_object(queryset)
        if obj.creator != self.request.user:
            raise Http404()
        return obj


class PackageCreate(CreateView):
    model = Package
    form_class = PackageCreateEditForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(PackageCreate, self).form_valid(form)


class PackageDetail(DetailView):
    model = Package


class PackageEdit(PackageEditMixin, UpdateView):
    model = Package
    form_class = PackageCreateEditForm


class PackageFlag(SingleObjectMixin, FormView):
    model = Package
    form_class = PackageFlagForm
    success_url = reverse_lazy('package_list')
    template_name = 'packages/package_flag.html'
    context_object_name = 'object'  # For consistency with other views.

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(PackageFlag, self).dispatch(request, *args, **kwargs)

    def send_flag_email(self, form):
        # TODO: Make it a Celery task.

        from django.core.mail import send_mail
        from django.template import Context, loader
        from django.conf import settings

        context = Context({
            'user': self.request.user,
            'user_url': self.request.build_absolute_uri(
                    self.request.user.get_absolute_url()),
            'package': self.object,
            'package_url': self.request.build_absolute_uri(
                    self.object.get_absolute_url()),
            'reason': form.cleaned_data['reason'],
        })
        managers = settings.FLAG_EMAIL_MANAGERS

        subject_template = 'packages/flag_email/subject.txt'
        body_text_template = 'packages/flag_email/body.txt'

        subject = loader.render_to_string(subject_template, context)
        subject = ''.join(subject.splitlines())
        body_text = loader.render_to_string(body_text_template, context)

        send_mail(
            subject=subject,
            message=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[manager[1] for manager in managers],
        )
        return True

    def form_valid(self, form):
        sent = self.send_flag_email(form)
        if sent:
            messages.success(self.request, 'Thanks for flagging {0}. We have '
                    'notified the administrators and they will review this '
                    'package shortly.'.format(self.object))
        else:
            messages.error(self.request, 'Sorry, an error occurred while '
                    'sending the flag email to administrators. Please try '
                    'again later.')
        return super(PackageFlag, self).form_valid(form)


class PackageList(ListView):
    model = Package
    paginate_by = 10
