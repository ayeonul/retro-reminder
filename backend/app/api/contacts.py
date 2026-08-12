from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate


router = APIRouter(prefix="/contacts", tags=["contacts"])


def get_contact_or_404(contact_id: int, db: Session) -> Contact:
    contact = db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="연락처를 찾을 수 없습니다.")
    return contact


@router.get("", response_model=list[ContactRead])
def list_contacts(query: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[Contact]:
    statement = select(Contact)
    if query and query.strip():
        keyword = f"%{query.strip()}%"
        statement = statement.where(or_(Contact.name.like(keyword), Contact.phone.like(keyword)))
    return list(db.scalars(statement.order_by(Contact.name, Contact.id)))


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)) -> Contact:
    contact = Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)) -> Contact:
    contact = get_contact_or_404(contact_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_contact_or_404(contact_id, db))
    db.commit()
