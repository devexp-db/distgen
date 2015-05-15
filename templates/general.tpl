{%- macro command(cmdinfo) -%}
{%- if cmdinfo.type == "pkg" -%}
{%- if cmdinfo.action in ["install", "reinstall"] -%}
{{ commands.pkginstaller[cmdinfo.action](cmdinfo.packages) }}
{%- else -%}
{{ commands.pkginstaller[cmdinfo.action]() }}
{%- endif -%}
{%- elif cmdinfo.type == "shell" -%}
{{ cmdinfo.action }}
{%- endif -%}
{%- endmacro -%}

{%- import "container/" + container.name + "/parts.tpl" as ctr with context -%}
{%- import "macros/system.macros" as macros -%}
{%- block content %}{% endblock -%}
