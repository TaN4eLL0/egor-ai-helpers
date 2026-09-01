---
topic: gradle-build-cache
verified: 2026-09-01
source: https://docs.gradle.org/current/userguide/build_cache.html
volatility: stable
---

Gradle build cache выключен по умолчанию: «By default, the build cache is not
enabled.»

Включается двумя документированными способами, других нет:

- флаг `--build-cache` в командной строке — только для текущего build;
- строка `org.gradle.caching=true` в `gradle.properties` — для всех build,
  пока не выключено явно через `--no-build-cache`.
