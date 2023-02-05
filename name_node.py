name = "<network>"
min_signed_per_window = <min_signed_per_window>
signed_blocks_window = <signed_blocks_window>

skipped_blocks_allowed = int( signed_blocks_window * ( (100 - min_signed_per_window) / 100 ) ) # не допуста кількість пропущених блоків
time_jail = skipped_blocks_allowed * 5.5 # відповідь в секундах
