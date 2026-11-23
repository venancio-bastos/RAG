"""Split corpus files into chunks that remember where they came from.

Every chunk keeps the exact character range it covers in the original
file, so ``text[chunk.start:chunk.end] == chunk.text`` always holds.
That range is what the search returns and what the moulinette grades.

Markdown / text strategy (decided in the Phase 1 design session):
    1. Cut the file at its headings ('#', '##', ...), ignoring '#' lines
       inside fenced code blocks.
    2. Glue sections that are too small (e.g. a heading with no content)
       to the section that follows.
    3. Split sections bigger than max_size at paragraph boundaries,
       filling "boxes" of paragraphs until the next one does not fit.
    4. If a single paragraph is bigger than max_size, cut it by force.
"""

import re
from typing import List, Tuple

from pydantic import BaseModel

# A (start, end) character range inside a file: text[start:end].
Span = Tuple[int, int]

# A heading is 1 to 6 '#' followed by a space, at the start of a line.
HEADING_RE = re.compile(r"#{1,6}\s")
# A blank line (possibly with spaces) separates two paragraphs.
BLANK_LINE_RE = re.compile(r"\n[ \t]*\n")
# A line starting with this opens or closes a fenced code block.
CODE_FENCE = "```"


class Chunk(BaseModel):
    """A piece of a corpus file and the character range it covers."""

    file_path: str
    start: int
    end: int
    text: str


def find_markdown_sections(text: str) -> List[Span]:
    """Return the character range of every Markdown section.

    A section starts at a heading line and ends where the next heading
    starts. The text before the first heading (if any) is a section too.
    Lines starting with '#' inside a fenced code block are code comments,
    not headings: ``in_code`` flips every time a ``` line is read.

    Args:
        text: Full content of the file.

    Returns:
        The (start, end) range of each section, in file order.
    """
    starts: List[int] = [0]
    in_code = False
    pos = 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(CODE_FENCE):
            in_code = not in_code
        elif not in_code and pos != 0 and HEADING_RE.match(line):
            starts.append(pos)
        pos += len(line)
    ends = starts[1:] + [len(text)]
    return list(zip(starts, ends))


def merge_small_sections(
    sections: List[Span], min_size: int, max_size: int
) -> List[Span]:
    """Glue every section shorter than min_size to the next section.

    A heading with no content (e.g. '## Using Tips') is useless as a
    chunk on its own. Merging only happens if the result still fits in
    max_size.

    Args:
        sections: Section ranges, in file order.
        min_size: Sections shorter than this are glued to the next one.
        max_size: A merged section can never be longer than this.

    Returns:
        The new list of section ranges.
    """
    merged: List[Span] = []
    for start, end in sections:
        if merged:
            prev_start, prev_end = merged[-1]
            prev_is_small = prev_end - prev_start < min_size
            if prev_is_small and end - prev_start <= max_size:
                merged[-1] = (prev_start, end)
                continue
        merged.append((start, end))
    return merged


def paragraph_ends(text: str, start: int, end: int) -> List[int]:
    """Return the positions inside [start, end) where a paragraph ends.

    A paragraph ends right after a blank line. The last position returned
    is always ``end``, so the whole range is covered.

    Args:
        text: Full content of the file.
        start: Start of the range to look at.
        end: End of the range to look at.

    Returns:
        Increasing list of cut positions, the last one being ``end``.
    """
    cuts = [match.end() for match in BLANK_LINE_RE.finditer(text, start, end)]
    if not cuts or cuts[-1] != end:
        cuts.append(end)
    return cuts


def hard_split(text: str, start: int, end: int, max_size: int) -> List[Span]:
    """Cut [start, end) into pieces of at most max_size characters.

    Only used when one paragraph alone is bigger than max_size. It cuts
    right after the last newline that fits, so no line is broken in the
    middle; if there is no newline, it cuts exactly at max_size.

    Args:
        text: Full content of the file.
        start: Start of the range to cut.
        end: End of the range to cut.
        max_size: Maximum length of each piece.

    Returns:
        The ranges of the pieces, in order.
    """
    spans: List[Span] = []
    while end - start > max_size:
        limit = start + max_size
        newline = text.rfind("\n", start, limit)
        cut = newline + 1 if newline > start else limit
        spans.append((start, cut))
        start = cut
    spans.append((start, end))
    return spans


def split_section(
    text: str, start: int, end: int, max_size: int
) -> List[Span]:
    """Split a section bigger than max_size at paragraph boundaries.

    Paragraphs are put in a "box" one after the other. When the next
    paragraph does not fit, the box is closed and a new one starts.

    Args:
        text: Full content of the file.
        start: Start of the section.
        end: End of the section.
        max_size: Maximum length of each piece.

    Returns:
        The ranges of the pieces, in order. Each one is <= max_size.
    """
    if end - start <= max_size:
        return [(start, end)]
    spans: List[Span] = []
    box_start = start
    box_end = start
    for cut in paragraph_ends(text, start, end):
        if cut - box_start <= max_size:
            box_end = cut  # this paragraph still fits in the box
            continue
        if box_end > box_start:
            spans.append((box_start, box_end))  # close the full box
            box_start = box_end
        if cut - box_start <= max_size:
            box_end = cut  # the paragraph starts the new box
        else:
            # One paragraph alone is too big: cut it by force.
            spans.extend(hard_split(text, box_start, cut, max_size))
            box_start = cut
            box_end = cut
    if box_end > box_start:
        spans.append((box_start, box_end))
    return spans


def chunk_markdown(
    text: str, file_path: str, max_size: int, min_size: int = 200
) -> List[Chunk]:
    """Split a Markdown (or plain text) file into chunks.

    Plain text files have no headings, so the whole file is one section
    that gets split by paragraphs.

    Args:
        text: Full content of the file.
        file_path: Path written in every chunk, exactly as in the corpus.
        max_size: Maximum length of a chunk, in characters.
        min_size: Sections shorter than this are glued to the next one.

    Returns:
        The chunks, in file order. Whitespace-only pieces are dropped.
    """
    sections = find_markdown_sections(text)
    sections = merge_small_sections(sections, min_size, max_size)
    chunks: List[Chunk] = []
    for section_start, section_end in sections:
        pieces = split_section(text, section_start, section_end, max_size)
        for start, end in pieces:
            piece = text[start:end]
            if piece.strip():
                chunks.append(
                    Chunk(file_path=file_path, start=start, end=end,
                          text=piece)
                )
    return chunks
