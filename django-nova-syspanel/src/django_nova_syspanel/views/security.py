from django import template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response
from django_nova_syspanel.forms import DisableProject
from django_nova_syspanel.forms import DisableIpAddress
from django_nova_syspanel.models import NovaResponseError, get_nova_admin_connection


@login_required
def index(request):
    disable_project_form = DisableProject()
    disable_ip_form = DisableIpAddress()
    return render_to_response('django_nova_syspanel/security/index.html',{
        'project_form':disable_project_form,
        'ip_form':disable_ip_form,
    },context_instance = template.RequestContext(request))

@login_required
def disable_project_credentials(request):
    if request.method == "POST":
        nova = get_nova_admin_connection()
        form = DisableProject(request.POST)
        if form.is_valid():
            name = form.cleaned_data['project_name']
            conn = nova.connection_for(settings.NOVA_ADMIN_USER, name)
            vpn = [x for x in nova.get_vpns() if x.project_id == name]
            if vpn:
                # NOTE(todd): Check, because it could already be shut-off
                vpn = vpn[0]
            try:
                nova.disable_project_credentials(name)
                if vpn and vpn.instance_id:
                    conn.terminate_instances([vpn.instance_id])
            except NovaResponseError, e:
                messages.error(request,
                               'Unable to disable project %s: %s - %s' %
                               (name, e.code, e.message))
                return redirect('syspanel_security')
            else:
                messages.success(request,
                                 'Project %s has been successfully disabled.' %
                                     form.cleaned_data['project_name'])
            return render_to_response(
                      'django_nova_syspanel/security/disable_project_credentials.html',
                      context_instance = template.RequestContext(request))
        else:
            messages.error(request, 'Invalid form data')
            return redirect('syspanel_security')
    else:
        return redirect('syspanel_security')

@login_required
def disable_ip(request):
    if request.method == "POST":
        conn = get_nova_admin_connection()
        form = DisableIpAddress(request.POST)
        if form.is_valid():
            try:
                conn.block_ips(form.cleaned_data['cidr'])
            except NovaResponseError, e:
                messages.error(request,
                               'Unable to block IPs range %s: %s %s' %
                               (form.cleaned_data['cidr'], e.code, e.message))
            else:
                messages.success(request,
                                 'IPs range %shas been successfully blocked' %
                                 form.cleaned_data['cidr'])

    return redirect('syspanel_security')


@login_required
def disable_public_ips(request):
    if request.method == "POST":
        try:
            nova = get_nova_admin_connection()
            nova.disable_all_floating_ips()
        except NovaResponseError, e:
            messages.error(request,
                           'Unable to shut off public IPs: %s - %s' %
                           (e.code, e.message,))
        else:
            messages.success(request, 'Public IPs have been turned off.')
    return redirect('syspanel_security')


@login_required
def disable_vpn(request):
    if request.method == "POST":
        nova = get_nova_admin_connection()
        conn = nova.connection_for(settings.NOVA_ADMIN_USER,
                                   settings.NOVA_PROJECT)
        try:
            collector = []
            for vpn in nova.get_vpns():
                if not vpn.instance_id:
                    continue
                collector.append(vpn)
                if len(collector) >= 5:
                    conn.terminate_instances([x.instance_id for x in collector])
                    collector = []
            if collector:
                conn.terminate_instances([x.instance_id for x in collector])
        except NovaResponseError, e:
            messages.error(request, 'Unable to shut off all VPNs: %s - %s' %
                                    (e.code, e.message,))
        else:
            messages.success(request, 'VPNs have been successfully turned off.')
        return redirect('syspanel_security')
    else:
        return redirect('syspanel_security')
