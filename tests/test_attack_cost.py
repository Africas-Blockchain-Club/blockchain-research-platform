import pytest

from data_analytics import attack_cost as ac


def test_new_stake_adds_to_the_total():
    # A third of the new total takes half of today's stake; two thirds takes twice it
    assert ac.coins_needed(900, 1 / 3) == pytest.approx(450)
    assert ac.coins_needed(900, 2 / 3) == pytest.approx(1800)


def test_more_than_the_unstaked_supply_is_reported_as_not_buyable():
    result = ac.price_attack(staked=900, share=2 / 3, price_usd=2, circulating=1000, volume_24h_usd=100)
    assert result["share_of_unstaked"] > 1
    assert result["days_of_volume"] == pytest.approx(36)


def test_fewest_validators_to_reach_a_third():
    assert ac.fewest_validators([50, 30, 10, 10], 1 / 3) == 1
    assert ac.fewest_validators([10] * 9, 1 / 3) == 3


@pytest.mark.parametrize("symbol, kind", [("BTC", "work"), ("XRP", "trust"), ("ETH", "stake"), ("TIA", "stake"), ("ADA", "stake")])
def test_only_stake_chains_are_priced(symbol, kind):
    assert ac.model_for(symbol).kind == kind


def test_a_chain_without_a_known_model_asks_the_user():
    assert ac.model_for("NEAR") is None


def test_user_text_cannot_forge_a_log_line():
    from dashboards.ui.components import one_line

    assert "\n" not in one_line("Celestia\nINFO fake entry") and "\r" not in one_line("a\rb")


PLATFORMS = {"solana": {"name": "Solana", "native_coin_id": "solana"},
             "base": {"name": "Base", "native_coin_id": "ethereum"},
             "osmosis": {"name": "Osmosis", "native_coin_id": "osmosis"}}


def test_a_token_is_attacked_through_the_chain_it_lives_on():
    arc = {"id": "ai-rig-complex", "symbol": "ARC", "name": "AI Rig Complex", "asset_platform_id": "solana"}
    found = ac.detect(arc, PLATFORMS)
    assert (found["host"], found["model"]) == ("SOL", "solana")
    assert ac.detect({"id": "x", "symbol": "X", "asset_platform_id": "base"}, PLATFORMS)["host"] == "ETH"


def test_a_chain_that_lists_itself_as_its_platform_is_not_a_token():
    osmo = {"id": "osmosis", "symbol": "OSMO", "asset_platform_id": "osmosis", "consensus_tags": ["Cosmos Ecosystem"]}
    found = ac.detect(osmo, PLATFORMS)
    assert (found["model"], found["host"]) == ("bft", None)


@pytest.mark.parametrize("coin, model", [
    ({"symbol": "DOGE", "hashing_algorithm": "Scrypt"}, "work"),
    ({"symbol": "NEAR", "consensus_tags": ["Proof of Stake (PoS)"]}, None),
    ({"symbol": "QQQ"}, None),
])
def test_clues_without_a_platform(coin, model):
    assert ac.detect(coin)["model"] == model
