# File: benchmarks/generate_chronodrift_60.py
# Version: 1.3.0 | Release Date: 2026-11-17
# EN: Generator for the ChronoDrift-Entity-60 longitudinal benchmark (60 episodes x 6 snapshots = 360 events).
# DE: Generator für den longitudinalen Benchmark ChronoDrift-Entity-60 (60 Episoden x 6 Zeitpunkte = 360 Ereignisse).

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


def build_chronodrift_60() -> Dict[str, Any]:
    """
    EN: Constructs 60 longitudinal multi-source episodes across 6 temporal snapshots
        to evaluate cross-source entity resolution, bitemporal state transitions,
        and proactive multi-horizon planning.
    DE: Erstellt 60 longitudinale quellenübergreifende Episoden über 6 Zeitpunkte
        zur Evaluierung von Entitätsauflösung, bitemporalen Zustandsübergängen
        und proaktiver Horizontplanung.
    """
    episodes: List[Dict[str, Any]] = []
    t0 = datetime(2026, 11, 1, 8, 0, tzinfo=timezone.utc)
    times = [(t0 + timedelta(days=7 * k)).isoformat() for k in range(6)]

    # ------------------------------------------------------------------
    # Class A: Cross-Lingual Entity Aliasing DE/EN (E01 - E10)
    # ------------------------------------------------------------------
    de_en_pairs = [
        ("DFG Schwerpunktprogramm Quantencomputing 2026", "DFG Priority Programme Quantum Computing 2026", "DFG"),
        ("DFG Forschungsgruppen Nachhaltige Transformation", "DFG Research Units Sustainable Transformation", "DFG"),
        ("BMBF Richtlinie KI-Nachwuchsgruppen 2026", "BMBF Guideline AI Junior Research Groups 2026", "BMBF"),
        ("DAAD Postdoktoranden-Programm PRIME 2026", "DAAD Postdoctoral Researchers International Mobility PRIME 2026", "DAAD"),
        ("DFG Graduiertenkollegs Ausschreibung 2026", "DFG Research Training Groups Call 2026", "DFG"),
        ("BMBF Verbundprojekte Batterieforschung Deutschland", "BMBF Collaborative Projects Battery Research Germany", "BMBF"),
        ("DFG Heisenberg-Programm Stipendien 2026", "DFG Heisenberg Programme Fellowships 2026", "DFG"),
        ("DAAD Gastdozenturen Internationale Hochschulen", "DAAD Visiting Professorships International Universities", "DAAD"),
        ("DFG Klinische Studien Förderprogramm 2026", "DFG Clinical Trials Funding Programme 2026", "DFG"),
        ("BMBF Quantentechnologien Anwendungsnetzwerke", "BMBF Quantum Technologies Application Networks", "BMBF"),
    ]
    for idx, (title_de, title_en, funder) in enumerate(de_en_pairs, start=1):
        eid = f"E{idx:02d}"
        dl = "2027-02-15"
        obs = [
            {
                "step": k + 1,
                "valid_time": times[k],
                "source_id": f"{funder.lower()}_{'de' if k % 2 == 0 else 'en'}",
                "raw_uri": f"https://{funder.lower()}.de/{'de' if k % 2 == 0 else 'en'}/call-{idx}",
                "title": title_de if k % 2 == 0 else title_en,
                "deadline_iso": dl,
                "attributes": {"funder": funder},
                "true_entity_key": f"{eid}_canonical",
            }
            for k in range(6)
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "A_CROSS_LINGUAL_ALIAS",
            "expected_unique_entities": 1,
            "expected_key_transitions": ["ALIAS_MERGED"],
            "expected_action_types": ["CONSOLIDATE_CROSS_SOURCE_METADATA"],
            "observations": obs,
        })

    # ------------------------------------------------------------------
    # Class B: Cross-Portal Syndication & URI Migration (E11 - E20)
    # ------------------------------------------------------------------
    for idx in range(11, 21):
        eid = f"E{idx:02d}"
        dl = "2027-03-01"
        t_primary = f"ERC Horizon Europe Cluster {idx - 10} Synergy Call 2027"
        t_syndicated = f"ERC Horizon Europe Cluster {idx - 10} Synergy Call 2027 — EU Funding Portal"
        obs = [
            {"step": 1, "valid_time": times[0], "source_id": "erc_portal", "raw_uri": f"https://erc.europa.eu/calls/c-{idx}", "title": t_primary, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
            {"step": 2, "valid_time": times[1], "source_id": "eu_tenders", "raw_uri": f"https://ec.europa.eu/tenders/topic-{idx}", "title": t_syndicated, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
            {"step": 3, "valid_time": times[2], "source_id": "erc_portal", "raw_uri": f"https://erc.europa.eu/calls/c-{idx}", "title": t_primary, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
            {"step": 4, "valid_time": times[3], "source_id": "erc_portal", "raw_uri": f"https://erc.europa.eu/archive-v2/calls/c-{idx}", "title": t_primary, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
            {"step": 5, "valid_time": times[4], "source_id": "eu_tenders", "raw_uri": f"https://ec.europa.eu/tenders/topic-{idx}", "title": t_syndicated, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
            {"step": 6, "valid_time": times[5], "source_id": "erc_portal", "raw_uri": f"https://erc.europa.eu/archive-v2/calls/c-{idx}", "title": t_primary, "deadline_iso": dl, "attributes": {"funder": "ERC"}, "true_entity_key": f"{eid}_canonical"},
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "B_URI_MIGRATION_SYNDICATION",
            "expected_unique_entities": 1,
            "expected_key_transitions": ["ALIAS_MERGED"],
            "expected_action_types": ["CONSOLIDATE_CROSS_SOURCE_METADATA"],
            "observations": obs,
        })

    # ------------------------------------------------------------------
    # Class C: Longitudinal Deadline Extension (E21 - E30)
    # ------------------------------------------------------------------
    for idx in range(21, 31):
        eid = f"E{idx:02d}"
        title = f"VolkswagenStiftung Momentum Track {idx - 20}"
        deadlines = ["2026-12-20", "2026-12-20", "2027-01-31", "2027-01-31", "2027-02-28", "2027-02-28"]
        obs = [
            {
                "step": k + 1,
                "valid_time": times[k],
                "source_id": "vw_stiftung",
                "raw_uri": f"https://volkswagenstiftung.de/p-{idx}",
                "title": title,
                "deadline_iso": deadlines[k],
                "attributes": {"funder": "VolkswagenStiftung"},
                "true_entity_key": f"{eid}_canonical",
            }
            for k in range(6)
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "C_DEADLINE_SHIFT",
            "expected_unique_entities": 1,
            "expected_key_transitions": ["DEADLINE_EXTENDED"],
            "expected_action_types": ["UPDATE_DEADLINE_RECORD"],
            "observations": obs,
        })

    # ------------------------------------------------------------------
    # Class D: Expiration & Seasonal Reopening (E31 - E40)
    # ------------------------------------------------------------------
    for idx in range(31, 41):
        eid = f"E{idx:02d}"
        title = f"Humboldt Research Fellowship Cohort {idx - 30}"
        deadlines = ["2026-11-10", "2026-11-10", "2026-11-10", "2026-11-10", "2027-04-15", "2027-04-15"]
        obs = [
            {
                "step": k + 1,
                "valid_time": times[k],
                "source_id": "humboldt",
                "raw_uri": f"https://humboldt-foundation.de/f-{idx}",
                "title": title,
                "deadline_iso": deadlines[k],
                "attributes": {"funder": "Humboldt"},
                "true_entity_key": f"{eid}_canonical",
            }
            for k in range(6)
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "D_EXPIRATION_REOPENING",
            "expected_unique_entities": 1,
            "expected_key_transitions": ["STATUS_EXPIRED", "STATUS_REOPENED"],
            "expected_action_types": ["ARCHIVE_EXPIRED_ENTITY", "DISPATCH_REOPENED_NOTICE"],
            "observations": obs,
        })

    # ------------------------------------------------------------------
    # Class E: Approaching Horizon Urgent Alerting (E41 - E50)
    # ------------------------------------------------------------------
    for idx in range(41, 51):
        eid = f"E{idx:02d}"
        title = f"Fritz Thyssen Project Grant Round {idx - 40}"
        obs = [
            {
                "step": k + 1,
                "valid_time": times[k],
                "source_id": "thyssen",
                "raw_uri": f"https://fritz-thyssen-stiftung.de/g-{idx}",
                "title": title,
                "deadline_iso": "2026-12-03",
                "attributes": {"funder": "Thyssen"},
                "true_entity_key": f"{eid}_canonical",
            }
            for k in range(6)
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "E_URGENT_HORIZON_SWEEP",
            "expected_unique_entities": 1,
            "expected_key_transitions": ["STATUS_EXPIRING_SOON", "STATUS_EXPIRED"],
            "expected_action_types": ["DISPATCH_URGENT_ALERT", "ARCHIVE_EXPIRED_ENTITY"],
            "observations": obs,
        })

    # ------------------------------------------------------------------
    # Class F: Hard Negative Institutional Homonyms (E51 - E60)
    # ------------------------------------------------------------------
    homonym_pairs = [
        ("DFG Sachbeihilfe Forschungsprojekte", "DFG Eigene Stelle Nachwuchsförderung", "DFG"),
        ("ERC Starting Grant Frontier Research", "ERC Synergy Grant Collaborative Teams", "ERC"),
        ("DAAD Jahresstipendien für Doktoranden", "DAAD Kurzstipendien für Forschungsaufenthalte", "DAAD"),
        ("BMBF KMU-innovativ Biotechnologie", "BMBF KMU-innovativ Photonik", "BMBF"),
        ("DFG Koselleck-Projekte Risikoreiche Forschung", "DFG Emmy Noether-Programm Nachwuchsgruppen", "DFG"),
        ("ERC Consolidator Grant Independent Leaders", "ERC Proof of Concept Innovation Grant", "ERC"),
        ("DAAD Forschungsstipendien Promotion Deutschland", "DAAD Wiedereinladungen Ehemalige Stipendiaten", "DAAD"),
        ("BMBF Validierung VIP+ Innovation", "BMBF GO-Bio Gründungsoffensive", "BMBF"),
        ("DFG Mercator-Fellowships Gastwissenschaftler", "DFG Reinhart Koselleck-Projekte", "DFG"),
        ("ERC Advanced Grant Established Investigators", "ERC Starting Grant Early Career", "ERC"),
    ]
    for idx, (prog_a, prog_b, funder) in enumerate(homonym_pairs, start=51):
        eid = f"E{idx:02d}"
        dl = "2027-03-15"
        obs = [
            {
                "step": k + 1,
                "valid_time": times[k],
                "source_id": f"{funder.lower()}_portal",
                "raw_uri": f"https://{funder.lower()}.org/{'a' if k % 2 == 0 else 'b'}-{idx}",
                "title": prog_a if k % 2 == 0 else prog_b,
                "deadline_iso": dl,
                "attributes": {"funder": funder},
                "true_entity_key": f"{eid}_{'prog_a' if k % 2 == 0 else 'prog_b'}",
            }
            for k in range(6)
        ]
        episodes.append({
            "episode_id": eid,
            "scenario_class": "F_HARD_NEGATIVE_HOMONYMS",
            "expected_unique_entities": 2,
            "expected_key_transitions": [],
            "expected_action_types": [],
            "observations": obs,
        })

    return {
        "dataset_name": "ChronoDrift-Entity-60",
        "version": "1.3.0",
        "release_date": "2026-11-17",
        "framework": "PyCognition v1.3.0",
        "total_episodes": len(episodes),
        "total_observations": sum(len(ep["observations"]) for ep in episodes),
        "episodes": episodes,
    }


def main() -> None:
    out_file = Path(__file__).resolve().parent / "chronodrift_entity_60.json"
    dataset = build_chronodrift_60()
    out_file.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Generated {dataset['total_episodes']} episodes "
        f"({dataset['total_observations']} temporal observations) -> {out_file}"
    )


if __name__ == "__main__":
    main()
