"""Estrutura inicial de baralhos para estudo, trabalho e projetos pessoais."""

from typing import List

RECOMMENDED_DECKS = [
    "ESAMC::Exatas",
    "Geral::Programação::Node.js",
]


def missing_recommended_decks(existing_decks: List[str]) -> List[str]:
    existing = set(existing_decks)
    return [deck for deck in RECOMMENDED_DECKS if deck not in existing]
