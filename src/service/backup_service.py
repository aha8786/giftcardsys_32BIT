import shutil
from datetime import datetime
from pathlib import Path

from config import settings


def create_backup() -> Path:
    """DB 파일을 backups/ 폴더에 타임스탬프 파일명으로 복사한다."""
    src = Path(settings.DB_PATH)
    if not src.exists():
        raise FileNotFoundError(f"DB 파일을 찾을 수 없습니다: {src}")

    backup_dir = Path(settings.BACKUP_DIR)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = backup_dir / f"giftcard_{timestamp}.db"
    shutil.copy2(src, dest)
    return dest


def list_backups() -> list[Path]:
    """백업 파일 목록을 최신순으로 반환한다."""
    backup_dir = Path(settings.BACKUP_DIR)
    if not backup_dir.exists():
        return []
    files = sorted(backup_dir.glob("giftcard_*.db"), reverse=True)
    return files
