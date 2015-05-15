{%- macro header() -%}
FROM {{ config.docker.registry + "/" + config.docker.from }}
MAINTAINER {% if spec.maintainer %}{{ spec.maintainer }}{% else %}{{ project.maintainer }}{% endif %}
{%- endmacro -%}

{%- macro expose() -%}
{% if spec.expose is defined -%}
EXPOSE {{ spec.expose | join(' ') }}

{% endif -%}
{%- endmacro -%}

{%- macro environment(envs) -%}
{%- if envs -%}
{%- for i in envs -%}
{%- if loop.first -%}
ENV {{ i.name }}="{{ i.value }}"
{%- else %} \
    {{ i.name }}="{{ i.value }}"
{%- endif -%}
{% endfor %}

{% endif -%}
{% endmacro -%}

{%- macro body_env() -%}
{%- set vars = [] -%}
{%- if container.name == "docker" -%}
{%-   set vars = vars + [{'name': 'container', 'value': 'docker'}] -%}
{%- endif -%}
{%- if spec.parts.envvars is defined  -%}
{%-   set vars = vars + spec.parts.envvars.data -%}
{%- endif -%}
{{ environment(vars) }}
{%- endmacro -%}


{%- macro execute(actions) -%}
{%- for i in actions -%}
{%- if loop.first -%}
RUN {{ command(i) }}{% else %} \
    && {{ command(i) }}
{%- endif %}
{%- endfor %}

{% endmacro -%}

{%- macro body_pkginstall() -%}
{%- set cmds = spec.parts.pkginstall.data -%}
{%- set cmds = cmds + [{"type": "pkg", "action": "cleancache"}] -%}
{{ execute(cmds) }}
{%- endmacro -%}

{%- macro body_commands() -%}
{{ execute(spec.parts.commands.data) }}
{%- endmacro -%}

{%- macro body_volumes() -%}
{%- if spec.parts.volumes is defined -%}
VOLUME
{%- for i in spec.parts.volumes.data %} \
    "{{ i.path }}"{% endfor %}
{% endif %}
{%- endmacro -%}


{%- macro add_tarball(file, dest="/") -%}
ADD "{{ file }}" "{{ dest -}}"

{% endmacro -%}


{%- macro add_files(files) %}
{%- if files.files is defined %}
{%- for i in files.files -%}
{%- if loop.first -%}
ADD "{{ i }}"{%- else %} \
    "{{ i }}"
{%- endif -%}
{%- endfor %} \
    "{{ files.dest }}"

{% endif -%}
{%- endmacro %}


{% macro body_addfiles() -%}
{%- if spec.parts.addfiles is defined and spec.parts.addfiles.data is defined -%}
{%- set files = spec.parts.addfiles.data -%}
{%- for i in files -%}
{%- if i.type == "files" -%}
{{ add_files(i) }}
{%- elif i.type == "tarball" -%}
{{ add_tarball(i.file) }}
{%- endif -%}
{%- endfor -%}
{%- endif -%}
{% endmacro %}


{%- macro entrypoint(entry) %}
ENTRYPOINT [{% for i in entry %}"{{ i }}"{% endfor %}]
{% endmacro %}


{%- macro footer() %}
{%- set user = "" -%}
{%- set entry = "" -%}
{%- set cmd = "container-start" -%}
{%- if spec.parts.footer is defined %}
{%- if spec.parts.footer.user is defined %}
{%- set user = "USER " + spec.parts.footer.user %}
{%- if spec.parts.footer.cmd is defined %}
{%- set cmd = spec.parts.footer.cmd -%}
{%- endif -%}
{%- endif %}
{%- endif %}
{{ expose() -}}
{% if user %}{{ user }}
{% endif -%}
{% if spec.parts.footer.entry is defined %}{{ entrypoint(spec.parts.footer.entry) }}
{% endif -%}
{%- if cmd %}CMD ["{{ cmd }}"]
{%- endif -%}
{%- endmacro -%}
