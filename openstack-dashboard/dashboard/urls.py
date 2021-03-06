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
URL patterns for the OpenStack Dashboard.
"""

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from registration import forms as reg_forms


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'dashboard.views.index', name='index'),
    url(r'^accounts/register/$',
        'registration.views.register',
        { 'form_class': reg_forms.RegistrationFormUniqueEmail },
        name='registration_register'),
    url(r'^accounts/', include('registration.urls')),
    url(r'^project/', include('django_nova.urls.project')),
    url(r'^region/', include('django_nova.urls.region')),
    url(r'^admin/project/', include('django_nova.urls.admin_project')),
    url(r'^admin/roles/', include('django_nova.urls.admin_roles')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^syspanel/', include('django_nova_syspanel.urls')),
)

urlpatterns += patterns('django.views.generic.simple',
    # TODO(devcamcar): Move permission denied template into django-nova.
    url(r'^denied/$',
        'direct_to_template',
        {'template': 'permission_denied.html'},
        name='dashboard_permission_denied'),
    url(r'^unavailable/$',
        'direct_to_template',
        {'template': 'unavailable.html'},
        name='nova_unavailable'),
)

urlpatterns += patterns('',
     (r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:],
      'django.views.static.serve',
      {'document_root': settings.MEDIA_ROOT,
       'show_indexes': True}),
 )
