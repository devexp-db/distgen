FROM {{ config.docker.registry }}/{{ config.docker.from }}

RUN čřž
RUN {{ spec.foo }}
