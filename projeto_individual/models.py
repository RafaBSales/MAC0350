from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional

class LinkReceitaTag(SQLModel, table=True):
    receita_id: Optional[int] = Field(
        default=None,
        foreign_key="receita.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
        ondelete="CASCADE"
    )


class Receita(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str

    tags: List["Tag"] = Relationship(
            back_populates="receitas",
            link_model=LinkReceitaTag,
            sa_relationship_kwargs={"passive_deletes": True}
            )

class Tag (SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True, unique=True)

    receitas: List["Receita"] = Relationship(
            back_populates="tags",
            link_model=LinkReceitaTag
            )
