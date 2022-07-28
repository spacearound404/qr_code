import subprocess
import logging


def mint_nft(address):
    cwd = '/opt/qr_code/smartcontracts/'
    formatted_address = address

    if address[:2].find('0x') == -1:
        formatted_address = f'0x{address}'

    cmd = ['npx', 'hardhat', 'mint', '--address', formatted_address]

    subprocess.run(cmd, cwd=cwd)