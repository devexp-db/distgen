{% extends "general.tpl" %}

{% block content %}
  {% block header %}
{{ ctr.header() }}
  {%   endblock %}

  {% block body %}
    {% block pkginstall %}
{{ ctr.body_env() + ctr.body_labels() -}}
      {% if spec.parts is defined %}
{{ ctr.body_pkginstall() +
   ctr.body_addfiles() +
   ctr.body_commands() +
   ctr.body_volumes()
-}}
      {% endif %}
    {% endblock %}
  {% endblock %}
  {% block footer %}
{{ ctr.footer() -}}
  {% endblock %}
{% endblock %}
