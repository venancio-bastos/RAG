"""Command-line entry point: uv run python -m src <command> [options]."""

import fire


class RagCLI:
    """RAG pipeline commands. Every command is still a stub (Phase 0)."""

    def index(self, max_chunk_size: int = 2000) -> None:
        """Chunk data/raw/ and save the index under data/processed/.

        Args:
            max_chunk_size: Maximum number of characters per chunk.
        """
        print(f"[index] not implemented yet (max_chunk_size={max_chunk_size})")

    def search(self, query: str, k: int = 10) -> None:
        """Print the top-k sources for a single query.

        Args:
            query: The question to search for.
            k: Number of sources to return.
        """
        print(f"[search] not implemented yet (query={query!r}, k={k})")

    def search_dataset(
        self, dataset_path: str, k: int = 10, save_directory: str = "."
    ) -> None:
        """Search every question of a dataset and save the results.

        Args:
            dataset_path: Path to a RagDataset JSON file.
            k: Number of sources per question.
            save_directory: Directory where the results JSON is written.
        """
        print(
            f"[search_dataset] not implemented yet (dataset_path="
            f"{dataset_path!r}, k={k}, save_directory={save_directory!r})"
        )

    def answer(self, query: str, k: int = 10) -> None:
        """Answer a single query using the retrieved context.

        Args:
            query: The question to answer.
            k: Number of sources to retrieve.
        """
        print(f"[answer] not implemented yet (query={query!r}, k={k})")

    def answer_dataset(
        self, student_search_results_path: str, save_directory: str = "."
    ) -> None:
        """Generate answers for every question of a search results file.

        Args:
            student_search_results_path: Path to a StudentSearchResults JSON.
            save_directory: Directory where the answers JSON is written.
        """
        print(
            f"[answer_dataset] not implemented yet (path="
            f"{student_search_results_path!r}, "
            f"save_directory={save_directory!r})"
        )

    def evaluate(
        self, student_search_results_path: str, dataset_path: str, k: int = 10
    ) -> None:
        """Report recall@k of search results against a ground-truth dataset.

        Args:
            student_search_results_path: Path to a StudentSearchResults JSON.
            dataset_path: Path to the AnsweredQuestions dataset JSON.
            k: Maximum number of sources considered per question.
        """
        print(
            f"[evaluate] not implemented yet (results="
            f"{student_search_results_path!r}, dataset={dataset_path!r}, "
            f"k={k})"
        )


def main() -> None:
    """Run the Fire CLI."""
    fire.Fire(RagCLI)


if __name__ == "__main__":
    main()
