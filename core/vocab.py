import random
from datetime import date
from core.db import get_session
from core.models import Vocab, VocabSeen, QuizAttempt
from sqlalchemy import select


def get_unquizzed_vocab_seen(user_id: int) -> VocabSeen | None:
    with get_session() as session:
        vs = session.execute(
            select(VocabSeen)
            .where(VocabSeen.user_id == user_id, VocabSeen.quizzed == False)
            .order_by(VocabSeen.shown_on.asc())
            .limit(1)
        ).scalar_one_or_none()
        if vs:
            session.expunge(vs)
        return vs


def build_recall_quiz(vocab_seen: VocabSeen) -> dict:
    with get_session() as session:
        correct_vocab = session.get(Vocab, vocab_seen.vocab_id)
        if not correct_vocab:
            return None

        distractors = session.execute(
            select(Vocab.meaning)
            .where(Vocab.active == True, Vocab.id != correct_vocab.id)
            .order_by(Vocab.id)
        ).scalars().all()

        if len(distractors) < 2:
            distractors = ["A different meaning entirely", "Something else completely"]

        options = [correct_vocab.meaning] + random.sample(distractors, min(2, len(distractors)))
        random.shuffle(options)

        return {
            "vocab_id": correct_vocab.id,
            "word": correct_vocab.word,
            "language": correct_vocab.language,
            "flag": correct_vocab.flag,
            "pronunciation": correct_vocab.pronunciation,
            "correct_meaning": correct_vocab.meaning,
            "options": options,
            "vocab_seen_id": vocab_seen.id,
        }


def record_quiz_attempt(user_id: int, quiz_type: str, question_ref: str, was_correct: bool | None):
    with get_session() as session:
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_type=quiz_type,
            question_ref=question_ref,
            was_correct=was_correct,
        )
        session.add(attempt)


def mark_vocab_quizzed(vocab_seen_id: int):
    with get_session() as session:
        vs = session.get(VocabSeen, vocab_seen_id)
        if vs:
            vs.quizzed = True


def get_new_vocab_for_user(user_id: int) -> Vocab | None:
    with get_session() as session:
        seen_ids = session.execute(
            select(VocabSeen.vocab_id).where(VocabSeen.user_id == user_id)
        ).scalars().all()

        unseen = session.execute(
            select(Vocab)
            .where(Vocab.active == True, ~Vocab.id.in_(seen_ids))
            .order_by(Vocab.id)
        ).scalars().all()

        if unseen:
            vocab = random.choice(unseen)
            session.expunge(vocab)
            return vocab

        all_vocab = session.execute(
            select(Vocab).where(Vocab.active == True)
        ).scalars().all()

        if all_vocab:
            vocab = random.choice(all_vocab)
            session.expunge(vocab)
            return vocab

        return None


def log_vocab_seen(user_id: int, vocab_id: int):
    today = date.today()
    with get_session() as session:
        exists = session.execute(
            select(VocabSeen).where(
                VocabSeen.user_id == user_id,
                VocabSeen.vocab_id == vocab_id,
                VocabSeen.shown_on == today
            )
        ).scalar_one_or_none()
        if not exists:
            vs = VocabSeen(user_id=user_id, vocab_id=vocab_id, shown_on=today)
            session.add(vs)


def get_vocab_accuracy(user_id: int) -> float:
    with get_session() as session:
        attempts = session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id, QuizAttempt.quiz_type == "vocab_recall")
        ).scalars().all()
        if not attempts:
            return 0.0
        correct = sum(1 for a in attempts if a.was_correct)
        return correct / len(attempts)