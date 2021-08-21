FROM mcr.microsoft.com/dotnet/aspnet:5.0-alpine
WORKDIR /app

COPY ./start.sh .
COPY ./out/ /app/

RUN apk add --no-cache icu-libs gnu-libiconv
ENV LD_PRELOAD /usr/lib/preloadable_libiconv.so
RUN apk add --no-cache harfbuzz pango librsvg gdk-pixbuf
RUN apk add libgdiplus ttf-dejavu ttf-droid ttf-freefont ttf-liberation ttf-ubuntu-font-family fontconfig --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/

RUN ln -s /usr/lib/librsvg-2.so.2 librsvg-2.so
RUN ln -s /usr/lib/libgobject-2.0.so.0 libgobject-2.0.so
RUN ln -s /usr/lib/libcairo.so.2 libcairo.so
RUN ln -s /usr/lib/libgdk_pixbuf-2.0.so.0 libgdk_pixbuf-2.0.so
RUN ln -s /usr/lib/libgdiplus.so.0 libgdiplus.so

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 COMPlus_JitTelemetry=0 COMPlus_legacyCorruptedStateExceptionsPolicy=1 COMPlus_legacyUnhandledExceptionPolicy=1 ASPNETCORE_ENVIRONMENT=Production LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

RUN adduser --system --home /app --shell /usr/sbin/nologin --no-create-home --disabled-password svghost

RUN mkdir -p /app/data
VOLUME /app/data

CMD ["./start.sh"]
