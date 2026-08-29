from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Float,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    pin_hash = Column(String(128), nullable=False)
    pin_salt = Column(String(32), nullable=False)
    adventurer_name = Column(String(128), nullable=True)
    prefix = Column(String(32), nullable=True)
    suffix = Column(String(32), nullable=True)
    theme_preference = Column(String(16), default="dark")
    spice_level = Column(String(16), default="mild")
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("Preference", back_populates="user", cascade="all, delete-orphan")
    quest_completions = relationship("QuestCompletion", back_populates="user", cascade="all, delete-orphan")
    vocab_seen = relationship("VocabSeen", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    daily_sessions = relationship("DailySession", back_populates="user", cascade="all, delete-orphan")


class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    axis_index = Column(Integer, nullable=False)
    option_a = Column(String(128), nullable=False)
    option_b = Column(String(128), nullable=False)

    user = relationship("User", back_populates="preferences")

    __table_args__ = (UniqueConstraint("user_id", "axis_index", name="uq_user_axis"),)


class Quest(Base):
    __tablename__ = "quests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    desc = Column(Text, nullable=False)
    category = Column(String(32), nullable=False)
    emoji = Column(String(16), nullable=False)
    assistance_text = Column(Text, nullable=True)
    day_type = Column(String(16), default="weekday")
    rarity = Column(String(16), default="common")
    spice_level = Column(String(16), default="mild")
    active = Column(Boolean, default=True)
    created_by_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    completions = relationship("QuestCompletion", back_populates="quest")


class QuestCompletion(Base):
    __tablename__ = "quest_completions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False, index=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(Date, index=True, nullable=False)

    user = relationship("User", back_populates="quest_completions")
    quest = relationship("Quest", back_populates="completions")

    __table_args__ = (Index("ix_user_completion_date", "user_id", "completion_date"),)


class Vocab(Base):
    __tablename__ = "vocab"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(64), nullable=False)
    flag = Column(String(8), nullable=False)
    word = Column(String(128), nullable=False, index=True)
    meaning = Column(Text, nullable=False)
    pronunciation = Column(String(128), nullable=True)
    active = Column(Boolean, default=True)

    seen_by = relationship("VocabSeen", back_populates="vocab")


class VocabSeen(Base):
    __tablename__ = "vocab_seen"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vocab_id = Column(Integer, ForeignKey("vocab.id"), nullable=False, index=True)
    shown_on = Column(Date, nullable=False, index=True)
    quizzed = Column(Boolean, default=False)

    user = relationship("User", back_populates="vocab_seen")
    vocab = relationship("Vocab", back_populates="seen_by")

    __table_args__ = (UniqueConstraint("user_id", "vocab_id", "shown_on", name="uq_user_vocab_date"),)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_type = Column(String(32), nullable=False)
    question_ref = Column(String(256), nullable=True)
    was_correct = Column(Boolean, nullable=True)
    answered_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_attempts")


class DailySession(Base):
    __tablename__ = "daily_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_date = Column(Date, nullable=False, index=True)
    vibe_check_done = Column(Boolean, default=False)
    vocab_recall_done = Column(Boolean, default=False)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=True)
    quest_completed = Column(Boolean, default=False)
    reroll_count = Column(Integer, default=0)
    spice_level_selected = Column(String(16), default="mild")

    user = relationship("User", back_populates="daily_sessions")
    quest = relationship("Quest")

    __table_args__ = (UniqueConstraint("user_id", "session_date", name="uq_user_session_date"),)


class AdminSetting(Base):
    __tablename__ = "admin_settings"

    key = Column(String(64), primary_key=True)
    value = Column(String(256), nullable=False)