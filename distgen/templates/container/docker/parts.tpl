{% macro header() %}
FROM {{ config.docker.registry + "/" + config.docker.from }}
MAINTAINER {% if spec.maintainer %}{{ spec.maintainer }}{% else %}{{ project.maintainer }}{% endif %}
{% endmacro %}

{% macro expose() %}
{% if spec.expose is defined %}

EXPOSE {{ spec.expose | join(' ') }}
{% endif %}
{% endmacro %}

{% macro variables(envs, type) %}
{% if envs %}
{% for i in envs %}
{% if loop.first %}{{ type }} {{ i.name }}="{{ i.value | replace('"', '\\"') }}"{% else %} \
    {{ i.name }}="{{ i.value | replace('"', '\\"') }}"{% endif %}
{% endfor %}
{% endif %}
{% endmacro %}

{% macro body_env() %}
{% set vars = [] %}
{% if container.name == "docker" %}
{%   set vars = vars + [{'name': 'container', 'value': 'docker'}] %}
{% endif %}
{% if spec.parts is defined and  spec.parts.envvars is defined  %}
{%   set vars = vars + spec.parts.envvars.data %}
{% endif %}
{{ variables(vars, 'ENV') }}
{% endmacro %}

{% macro body_labels() %}
{% if spec.parts is defined and  spec.parts.labels is defined  %}

{{ variables(spec.parts.labels.data, 'LABEL') }}
{% endif %}
{% endmacro %}

{% macro execute(actions) %}
{% for i in actions %}
{% if loop.first %}

RUN {{ command(i) }}{% else %} \
    && {{ command(i) }}{% endif %}
{% endfor %}
{% endmacro %}

{% macro body_pkginstall() %}
{% if spec.parts.pkginstall is defined and spec.parts.pkginstall.data is defined %}
{% set cmds = spec.parts.pkginstall.data %}
{% set cmds = cmds + [{"type": "pkg", "action": "cleancache"}] %}
{{ execute(cmds) }}
{% endif %}
{% endmacro %}

{% macro body_commands() %}
{% if spec.parts.commands is defined and spec.parts.commands.data is defined %}
{{ execute(spec.parts.commands.data) }}
{% endif %}
{% endmacro %}

{% macro body_volumes() %}
{% if spec.parts.volumes is defined %}

VOLUME \
{% for i in spec.parts.volumes.data %}
{% if loop.last %}
    "{{ i.path }}"
{% else %}
    "{{ i.path }}" \
{% endif %}
{% endfor %}
{% endif %}
{% endmacro %}


{% macro add_tarball(file, dest="/") %}

ADD "{{ file }}" "{{ dest }}"
{% endmacro %}


{% macro add_files(files) %}
{% if files.files is defined %}
{% for i in files.files %}
{% if loop.first %}

ADD "{{ i }}"{% else %} \
    "{{ i }}"{% endif %}
{% endfor %} \
    "{{ files.dest }}"
{% endif %}
{% endmacro %}


{% macro body_addfiles() %}
{% if spec.parts.addfiles is defined and spec.parts.addfiles.data is defined %}
{% set files = spec.parts.addfiles.data %}
{% for i in files %}
{% if i.type == "files" %}
{{ add_files(i) -}}
{% elif i.type == "tarball" %}
{{ add_tarball(i.file) -}}
{% endif %}
{% endfor %}
{% endif %}
{% endmacro %}

{% macro cmd_footer(what, array) %}
{{ what }} [
{%- for i in array %}
{% if loop.last %}"{{ i }}"{% else %}"{{ i }}", {% endif %}
{% endfor -%}
]
{% endmacro %}

{% macro footer() %}
{% set user = "" %}
{% set entry = "" %}
{% set cmd = ["container-start"] %}
{% if spec.parts is defined and spec.parts.footer is defined %}
{% if spec.parts.footer.user is defined %}
{% set user = "USER " + spec.parts.footer.user %}
{% endif %}
{% if spec.parts.footer.cmd is defined %}
{% set cmd = spec.parts.footer.cmd %}
{% endif %}
{% endif %}
{{ expose() }}
{% if user %}{{ user }}
{% endif %}
{% if spec.parts is defined and spec.parts.footer is defined and spec.parts.footer.entry is defined %}
{{ cmd_footer("ENTRYPOINT", spec.parts.footer.entry) -}}
{% endif %}
{% if cmd %}
{{ cmd_footer("CMD", cmd) -}}
{% endif %}
{% endmacro %}
