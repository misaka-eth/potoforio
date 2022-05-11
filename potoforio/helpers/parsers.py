def parse_float(float_str: str, normal_power: [int, None] = None) -> (int, int):
    """
    Parse float to int, and it's 10^power.
    Normalize it to normal_power if given.
    Example: 44.887088640175348549 -> (44887088640175348549, 18)
    """
    # Correct process 0
    if float_str == '0':
        return 0, 0

    # Split
    if float_str.count('.'):
        before, after = float_str.split(".")
    else:
        before = float_str
        after = ''

    # Make
    base = int(f'{before}{after}')

    if normal_power is not None:
        return normalize_power(base=base, power=len(after), normal_power=normal_power), len(after)

    return base, len(after)


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

    return base

