from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.memo import Memo
from app.schemas.memo import MemoCreate, MemoRead, MemoUpdate


router = APIRouter(prefix="/memos", tags=["memos"])


def get_memo_or_404(memo_id: int, db: Session) -> Memo:
    memo = db.get(Memo, memo_id)
    if memo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="메모를 찾을 수 없습니다.")
    return memo


@router.get("", response_model=list[MemoRead])
def list_memos(db: Session = Depends(get_db)) -> list[Memo]:
    return list(db.scalars(select(Memo).order_by(Memo.updated_at.desc(), Memo.id.desc())))


@router.get("/{memo_id}", response_model=MemoRead)
def get_memo(memo_id: int, db: Session = Depends(get_db)) -> Memo:
    return get_memo_or_404(memo_id, db)


@router.post("", response_model=MemoRead, status_code=status.HTTP_201_CREATED)
def create_memo(payload: MemoCreate, db: Session = Depends(get_db)) -> Memo:
    memo = Memo(**payload.model_dump())
    db.add(memo)
    db.commit()
    db.refresh(memo)
    return memo


@router.patch("/{memo_id}", response_model=MemoRead)
def update_memo(memo_id: int, payload: MemoUpdate, db: Session = Depends(get_db)) -> Memo:
    memo = get_memo_or_404(memo_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(memo, field, value)
    db.commit()
    db.refresh(memo)
    return memo


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memo(memo_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_memo_or_404(memo_id, db))
    db.commit()
