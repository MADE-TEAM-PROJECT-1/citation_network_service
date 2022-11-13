from email.policy import default
from uuid import uuid1
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Integer, Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from app.api.database import Base


text_keywords = Table(
    "text_keywords",
    Base.metadata,
    Column("text_keywords_id", UUID(as_uuid=True), primary_key=True, default=uuid1),
    Column("text_id", ForeignKey("text.id")),
    Column("keyword_id", ForeignKey("keywords.id")),
)

text_author = Table(
    "text_author",
    Base.metadata,
    Column("author_keywords_id", UUID(as_uuid=True), primary_key=True, default=uuid1),
    Column("text_id", ForeignKey("text.id")),
    Column("author_id", ForeignKey("author.id")),
    schema="citation_network",
)

text_fos = Table(
    "text_fos",
    Base.metadata,
    Column("text_fos_id", UUID(as_uuid=True), primary_key=True, default=uuid1),
    Column("fos_id", ForeignKey("fos.id")),
    Column("text_id", ForeignKey("text.id")),
    schema="citation_network",
)

org_author = Table(
    "org_author",
    Base.metadata,
    Column("org_author_id", UUID(as_uuid=True), primary_key=True, default=uuid1),
    Column("org_id", ForeignKey("org.id")),
    Column("author_id", ForeignKey("author.id")),
    schema="citation_network",
)

text_tags = Table(
    "text_tags",
    Base.metadata,
    Column("tag_text_id", UUID(as_uuid=True), primary_key=True, default=uuid1),
    Column("tag_id", ForeignKey("tags.id")),
    Column("text_id", ForeignKey("text.id")),
    schema="citation_network",
)


class Text(Base):
    __tablename__ = "text"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    title = Column(String, index=True)
    year = Column(Integer, nullable=True)
    n_citation = Column(Integer, nullable=True, default=0)
    abstract = Column(String, nullable=True)
    venue_name = Column(String)

    keywords = relationship("Keyword", secondary=text_keywords, back_populates="texts", )
    authors = relationship("Author", secondary=text_author, back_populates="texts")
    fos = relationship("Fos", secondary=text_fos, back_populates="texts")
    tags = relationship("Tags", secondary=text_tags, back_populates="texts")


class Citation(Base):
    __tablename__ = "citation"
    __table_args__ = {"schema": "citation_network"}

    citation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    text_id_from = Column(UUID(as_uuid=True), ForeignKey("text.id"))
    text_from = relationship(
        "Text", backref="citation_list", primaryjoin=(Text.id == text_id_from)
    )
    text_id_to = Column(UUID(as_uuid=True), ForeignKey("text.id"))
    text_to = relationship(
        "Text", backref="citited_in_list", primaryjoin=(Text.id == text_id_to)
    )


class Keyword(Base):
    __tablename__ = "keywords"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    name = Column(String, unique=True, index=True)

    texts = relationship("Text", secondary=text_keywords, back_populates="keywords")


class Author(Base):
    __tablename__ = "author"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    name = Column(String, index=True)

    texts = relationship("Text", secondary=text_author, back_populates="authors")
    orgs = relationship("Org", secondary=org_author, back_populates="authors")


class Fos(Base):
    __tablename__ = "fos"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    name = Column(String, unique=True, index=True)

    texts = relationship("Text", secondary=text_fos, back_populates="fos")


class Org(Base):
    __tablename__ = "org"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    name = Column(String)

    authors = relationship("Author", secondary=org_author, back_populates="orgs")

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)

    login = Column(String, index = True, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("author.id"))
    email = Column(String)

class Tags(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "citation_network"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid1)
    name = Column(String, unique=True, index=True)

    texts = relationship("Text", secondary=text_tags, back_populates="tags")