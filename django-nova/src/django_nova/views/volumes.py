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
Views for managing Nova volumes.
"""

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render_to_response
from django_nova import exceptions
from django_nova import forms
from django_nova import shortcuts
from django_nova.exceptions import handle_nova_error


@login_required
@handle_nova_error
def index(request, project_id):
    project = shortcuts.get_project_or_404(request, project_id)
    volumes = project.get_volumes()

    return render_to_response('django_nova/volumes/index.html', {
        'create_form': forms.CreateVolumeForm(),
        'attach_form': forms.AttachVolumeForm(project),
        'region': project.region,
        'project': project,
        'volumes': volumes,
    }, context_instance = template.RequestContext(request))


@login_required
@handle_nova_error
def add(request, project_id):
    project = shortcuts.get_project_or_404(request, project_id)

    if request.method == 'POST':
        form = forms.CreateVolumeForm(request.POST)
        if form.is_valid():
            try:
                volume = project.create_volume(form.cleaned_data['size'],
                                               form.cleaned_data['nickname'],
                                               form.cleaned_data['description'])
            except exceptions.NovaApiError, e:
                messages.error(request,
                               'Unable to create volume: %s' % e.message)
            else:
                messages.success(request,
                                 'Volume %s %s has been successfully created.' %
                                 (volume.id, volume.displayName))
        else:
            volumes = project.get_volumes()

            return render_to_response('django_nova/volumes/index.html', {
                'create_form': form,
                'attach_form': forms.AttachVolumeForm(project),
                'region': project.region,
                'project': project,
                'volumes': volumes,
            }, context_instance = template.RequestContext(request))

    return redirect('nova_volumes', project_id)


@login_required
@handle_nova_error
def delete(request, project_id, volume_id):
    project = shortcuts.get_project_or_404(request, project_id)

    if request.method == 'POST':
        try:
            project.delete_volume(volume_id)
        except exceptions.NovaApiError, e:
            messages.error(request,
                           'Unable to delete volume: %s' % e.message)
        else:
            messages.success(request,
                             'Volume %s has been successfully deleted.'
                             % volume_id)

    return redirect('nova_volumes', project_id)


@login_required
@handle_nova_error
def attach(request, project_id):
    project = shortcuts.get_project_or_404(request, project_id)

    if request.method == 'POST':
        form = forms.AttachVolumeForm(project, request.POST)
        if form.is_valid():
            try:
                project.attach_volume(
                    form.cleaned_data['volume'],
                    form.cleaned_data['instance'],
                    form.cleaned_data['device']
                )
            except exceptions.NovaApiError, e:
                messages.error(request,
                               'Unable to attach volume: %s' % e.message)
            else:
                messages.success(request,
                                 'Volume %s is scheduled to be attached.  If '
                                 'it doesn\'t become attached in two '
                                 'minutes,  please try again (you may need to '
                                 'specify a different device).' %
                                 form.cleaned_data['volume'])
        else:
            volumes = project.get_volumes()

            return render_to_response('django_nova/volumes/index.html', {
                'create_form': forms.CreateVolumeForm(),
                'attach_form': form,
                'region': project.region,
                'project': project,
                'volumes': volumes,
            }, context_instance = template.RequestContext(request))

    return redirect('nova_volumes', project_id)


@login_required
@handle_nova_error
def detach(request, project_id, volume_id):
    project = shortcuts.get_project_or_404(request, project_id)

    if request.method == 'POST':
        try:
            project.detach_volume(volume_id)
        except exceptions.NovaApiError, e:
            messages.error(request,
                           'Unable to detach volume: %s' % e.message)
        else:
            messages.success(request,
                             'Volume %s has been successfully detached.' %
                             volume_id)

    return redirect('nova_volumes', project_id)
