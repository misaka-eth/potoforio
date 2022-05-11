def parse_float(float_str: str) -> (int, int):
    """
    Parse float to int, and it's 10^power
    Example: 44.887088640175348549 -> (44887088640175348549, 18)
    """
    # Correct process 0
    if float_str == '0':
        return 0, 0

    # Split
    before, after = float_str.split(".")

    # Check is it's can be parsed to int
    int(before)
    int(after)

    # Make
    full = int(f'{before}{after}')

    return full, len(after)


def normalize_power(base: int, power: int, normal_power: int) -> (int, int):
    """
    Return base in 10^normal_power.
    Can LOSE PRECISION if power>normal_power
    """
    power_diff = normal_power - power

    if power_diff > 0:
        base = base * pow(10, power_diff)

    if power_diff < 0:
        base = int(base / pow(10, -power_diff))

    return base, normal_power
