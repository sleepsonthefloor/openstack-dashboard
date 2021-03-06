# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing Nova security groups.
"""

from django import http
from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response
from django_nova import exceptions
from django_nova import forms
from django_nova.exceptions import handle_nova_error
from django_nova.shortcuts import get_project_or_404


@login_required
@handle_nova_error
def index(request, project_id):
    project = get_project_or_404(request, project_id)
    securitygroups = project.get_security_groups()

    return render_to_response('django_nova/securitygroups/index.html', {
        'create_form': forms.CreateSecurityGroupForm(project),
        'project': project,
        'securitygroups': securitygroups,
    }, context_instance = template.RequestContext(request))


@login_required
@handle_nova_error
def detail(request, project_id, group_name):
    project = get_project_or_404(request, project_id)
    securitygroup = project.get_security_group(group_name)

    if not securitygroup:
        raise http.Http404

    return render_to_response('django_nova/securitygroups/detail.html', {
        'authorize_form': forms.AuthorizeSecurityGroupRuleForm(),
        'project': project,
        'securitygroup': securitygroup,
    }, context_instance = template.RequestContext(request))


@login_required
@handle_nova_error
def add(request, project_id):
    project = get_project_or_404(request, project_id)

    if request.method == 'POST':
        form = forms.CreateSecurityGroupForm(project, request.POST)
        if form.is_valid():
            try:
                project.create_security_group(
                    form.cleaned_data['name'],
                    form.cleaned_data['description'])
            except exceptions.NovaApiError, e:
                messages.error(request,
                               'Unable to create security group: %s' % e.message)
            else:
                messages.success(
                    request,
                    'Security Group %s has been succesfully created.' % \
                    form.cleaned_data['name'])
        else:
            securitygroups = project.get_security_groups()

            return render_to_response('django_nova/securitygroups/index.html', {
                'create_form': form,
                'project': project,
                'securitygroups': securitygroups,
            }, context_instance = template.RequestContext(request))

    return redirect('nova_securitygroups', project_id)


@login_required
@handle_nova_error
def authorize(request, project_id, group_name):
    project = get_project_or_404(request, project_id)

    if request.method == 'POST':
        form = forms.AuthorizeSecurityGroupRuleForm(request.POST)
        if form.is_valid():
            try:
                project.authorize_security_group(
                    group_name = group_name,
                    ip_protocol = form.cleaned_data['protocol'],
                    from_port = form.cleaned_data['from_port'],
                    to_port = form.cleaned_data['to_port'])
            except exceptions.NovaApiError, e:
                messages.error(request,
                               'Unable to authorize: %s' % e.message)
            else:
                messages.success(
                    request,
                    'Security Group %s: Access to %s ports %d - %d'
                    ' has been authorized.' %
                        (group_name,
                         form.cleaned_data['protocol'],
                         form.cleaned_data['from_port'],
                         form.cleaned_data['to_port']))
        else:
            securitygroup = project.get_security_group(group_name)

            if not securitygroup:
                raise http.Http404

            return render_to_response('django_nova/securitygroups/detail.html', {
                'authorize_form': form,
                'project': project,
                'securitygroup': securitygroup,
            }, context_instance = template.RequestContext(request))

    return redirect('nova_securitygroups_detail', project_id, group_name)


@login_required
@handle_nova_error
def revoke(request, project_id, group_name):
    project = get_project_or_404(request, project_id)

    if request.method == 'POST':
        try:
            project.revoke_security_group(
                group_name = group_name,
                ip_protocol = request.POST['protocol'],
                from_port = request.POST['from_port'],
                to_port = request.POST['to_port'])
        except exceptions.NovaApiError, e:
            messages.error(request, 'Unable to revoke: %s' % e.message)
        else:
            messages.success(
                request,
                'Security Group %s: Access to %s ports %s - %s '
                'has been revoked.' %
                   (group_name,
                    request.POST['protocol'],
                    request.POST['from_port'],
                    request.POST['to_port']))

    return redirect('nova_securitygroups_detail', project_id, group_name)


@login_required
@handle_nova_error
def delete(request, project_id, group_name):
    project = get_project_or_404(request, project_id)

    if request.method == 'POST':
        try:
            project.delete_security_group(name=group_name)
        except exceptions.NovaApiError, e:
            messages.error(
                request,
                'Unable to delete security group: %s' % e.message)
        else:
            messages.success(request,
                             'Security Group %s was successfully deleted.' %
                             group_name)

    return redirect('nova_securitygroups', project_id)
