#!/usr/bin/env bash
set -uo pipefail

CONF="${HOME}/.config/egor-ai-helpers/install.conf"
[[ -f "$CONF" ]] || exit 0
INSTALL_DIR=$(grep '^INSTALL_DIR=' "$CONF" | head -1 | cut -d= -f2-)
[[ -x "${INSTALL_DIR}/install.sh" ]] || exit 0

"${INSTALL_DIR}/install.sh" --check && exit 0

if ! "${INSTALL_DIR}/install.sh" --quiet; then
    echo "## egor-ai rules are out of date and the refresh failed"
    echo "Run \`${INSTALL_DIR}/install.sh\` by hand; the egor-ai block loaded into this session is stale."
    exit 0
fi

echo "## egor-ai rules were out of date"
echo "claude/rules/ changed after the last install, so the egor-ai block loaded into this session is stale. It has been refreshed on disk; the current rules below supersede the block loaded earlier."
echo
sed -n '/<!-- egor-ai:start -->/,/<!-- egor-ai:end -->/p' "${HOME}/.claude/CLAUDE.md"
