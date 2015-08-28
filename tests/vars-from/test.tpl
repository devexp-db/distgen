{%- for i in macros | dictsort -%}
{{- i[0] }}: {{ i[1] }}
{% endfor -%}
