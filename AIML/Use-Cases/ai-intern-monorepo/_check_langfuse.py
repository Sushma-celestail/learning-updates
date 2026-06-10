import sys, os
sys.path.insert(0, '.')

# Force-read .env directly (bypass setdefault)
from pathlib import Path
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ[k.strip()] = v.strip().strip('"').strip("'")

pk = os.getenv('LANGFUSE_PUBLIC_KEY', '')
sk = os.getenv('LANGFUSE_SECRET_KEY', '')
print(f'PUBLIC_KEY : {pk[:15]}... (len={len(pk)})' if pk else 'PUBLIC_KEY : EMPTY')
print(f'SECRET_KEY : {sk[:15]}... (len={len(sk)})' if sk else 'SECRET_KEY : EMPTY')

from shared.observability.langfuse_cb import get_langfuse_handler
handler = get_langfuse_handler()
print('Langfuse handler:', 'CREATED ✅' if handler else 'None (keys not loaded)')
