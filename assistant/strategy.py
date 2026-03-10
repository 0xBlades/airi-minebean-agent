"""
Minebean Logic & Strategy Engine
Calculates Expected Value (EV) and decides which blocks to deploy.
"""

def calculate_ev(price_data: dict, current_round: dict, total_bet_eth: float) -> float:
    """
    Calculate the Expected Value (EV) of a round.
    Net EV ≈ BEAN_value + Beanpot_EV - (ETH_deployed * effective_house_edge)
    """
    try:
        # Parse BEAN price in Native ETH
        bean_price_eth = float(price_data.get("bean", {}).get("priceNative", 0))
        
        # 1 BEAN per round
        bean_value = 1.0 * bean_price_eth

        # Beanpot probability (1/777 chance)
        beanpot_raw = float(current_round.get("beanpotPool", 0)) / 1e18
        beanpot_ev = (1 / 777.0) * beanpot_raw * bean_price_eth

        # Effective house edge logic (1% admin from everyone, 10% from losers)
        # For simplicity, we assume an ~11% total leak in the worst case
        effective_house_edge = 0.11
        
        net_ev = bean_value + beanpot_ev - (total_bet_eth * effective_house_edge)
        return net_ev
    except Exception as e:
        print(f"[Strategy] EV calculation error: {e}")
        return -1.0

def select_best_blocks(current_round: dict, num_blocks: int = 10, prev_winner_block: int = -1) -> list[int]:
    """
    Select blocks by excluding the previous round's winning block.
    """
    import random
    
    # Available blocks are 0 to 24
    available_blocks = set(range(0, 25))
    
    # Remove the previous winner if it's valid
    if 0 <= prev_winner_block <= 24:
        available_blocks.discard(prev_winner_block)
        
    available_blocks = list(available_blocks)
    
    # Take random N blocks from the remaining pool
    return random.sample(available_blocks, min(num_blocks, len(available_blocks)))
