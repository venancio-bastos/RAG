"""Pydantic data models exchanged between the pipeline stages.

These follow the models defined in the subject. Extra fields may be added
later if the implementation needs them.
"""

import uuid
from typing import List

from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """A location inside a corpus file: a path and a character range."""

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """A question without an answer. The id is generated if missing."""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """A question with its reference sources and answer."""

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """A dataset of questions, answered or not."""

    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """The sources retrieved for one question."""

    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """The sources retrieved for one question plus the generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Output file of the search_dataset command."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Output file of the answer_dataset command."""

    search_results: List[MinimalAnswer]
    k: int
