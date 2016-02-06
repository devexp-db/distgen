{%- macro command(cmdinfo) -%}
{%- if cmdinfo.type == "pkg" -%}
{%- if cmdinfo.action in ["install", "reinstall", "update"] -%}
{{ commands.pkginstaller[cmdinfo.action](cmdinfo.packages) }}
{%- else -%}
{{ commands.pkginstaller[cmdinfo.action]() }}
{%- endif -%}
{%- elif cmdinfo.type == "shell" -%}
{{ cmdinfo.action }}
{%- endif -%}
{%- endmacro -%}

{%- import "container/" + container.name + "/parts.tpl" as ctr with context -%}
{%- block content %}{% endblock -%}
