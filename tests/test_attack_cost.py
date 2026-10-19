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
