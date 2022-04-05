import subprocess


def mint_nft(address):
    formatted_address = address

    if address[:2].find('0x') == -1:
        formatted_address = f'0x{address}'

    subprocess.run(['npx', 'hardhat', 'mint', '--address', formatted_address])