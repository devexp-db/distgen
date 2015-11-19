{%- extends "general.tpl" -%}
{%- block content -%}

Basic yum commands:
-------------------
{{ commands.pkginstaller.install(["PKG"]) }}
{{ commands.pkginstaller.reinstall(["PKG"]) }}
{{ commands.pkginstaller.cleancache() }}
{{ commands.pkginstaller.remove(["a", "b"]) }}

Docs test:
----------
{{ commands.pkginstaller.install(["PKG"], {'docs': True}) }}
{{ commands.pkginstaller.install(["PKG"], {'docs': False}) }}

Interactive test:
-----------------
{{ commands.pkginstaller.install(["PKG"], {'interactive': True}) }}
{{ commands.pkginstaller.install(["PKG"], {'interactive': False}) }}
{% endblock %}
