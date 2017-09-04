FROM {{ config.docker.from }}

LABEL MAINTAINER ...

ENV NAME=mycontainer VERSION=0 RELEASE=1 ARCH=x86_64

LABEL summary="A container that tells you how awesome it is." \
      com.redhat.component="$NAME" \
      version="$VERSION" \
      release="$RELEASE.$DISTTAG" \
      architecture="$ARCH" \
      usage="docker run -p 9000:9000 mycontainer" \
      help="Runs mycontainer, which listens on port 9000 and tells you how awesome it is. No dependencies." \
      description="{{ spec.description }}" \
      vendor="{{ spec.vendor }}" \
      org.fedoraproject.component="postfix" \
      authoritative-source-url="{{ spec.authoritative_source_url }}" \
      io.k8s.description="{{ spec.description }}" \
      io.k8s.display-name="Awesome container with SW version {{ spec.software_version }}" \
      io.openshift.expose-services="9000:http" \
      io.openshift.tags="some,tags"

EXPOSE 9000

# We don't actually use the "software_version" here, but we could,
#  e.g. to install a module with that ncat version
RUN {{ commands.pkginstaller.install(['nmap-ncat']) }} && \
    {{ commands.pkginstaller.cleancache() }}

RUN echo {{ spec.spam }}
RUN echo {{ spec.version }}

# add help file
#  NOTE: this file is rendered from help.md, it's not actually templated (help.md is)
COPY root/help.1 /
COPY script.sh /usr/bin/

CMD ["/usr/bin/script.sh"]
