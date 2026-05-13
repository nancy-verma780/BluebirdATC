import os

from bluebird_dt.scenario_manager.springfield import SpringfieldScenarioManager
from bluebird_dt.utility.paths import LOG_DIR


def list_sim_scenario_categories() -> list[str]:
    """
    List the available scenario categories.
    """

    return ["Artificial", "Springfield", "Infinite", "Flight School"]


def list_sim_scenarios(category: str) -> list[str]:
    """
    List the scenarios in a given category.
    """

    # make directory for replay files if it doesn't exist already
    os.makedirs(LOG_DIR, exist_ok=True)

    if category == "Springfield":
        return SpringfieldScenarioManager.list_scenarios()

    if category == "Artificial":
        return [
            "I-Sector Two Aircraft",
            "X-Sector Two Aircraft",
            "Y-Sector Two Aircraft",
        ]

    if category == "Infinite":
        return [
            "X-Sector",
            "Xplus-Sector",
            "Y-Sector",
            "I-Sector",
            "Two Sector",
        ]

    if category == "Flight School":
        return ["Xplus-Sector"]

    raise ValueError(f"Unknown scenario category: {category}")
