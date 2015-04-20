{%- macro yum_action(packages, action) -%}
yum {{ action }} {{ packages | join(' ') }} -y
{%- endmacro -%}

{%- macro install(packages) -%}
{{ yum_action(packages, 'install') }}
{%- endmacro -%}

{%- macro reinstall(packages) -%}
{{ yum_action(packages, 'reinstall') }}
{%- endmacro -%}

{%- macro cleancache() -%}
yum clean all --enablerepo='*'
{%- endmacro -%}

{%- macro systemupdate() -%}
yum update -y
{%- endmacro -%}
