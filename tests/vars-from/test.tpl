{%- for i in dirs | dictsort -%}
{{- i[0] }}: {{ i[1] }}
{% endfor -%}
