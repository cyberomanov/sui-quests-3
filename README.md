1. настройка конфига, количество транзакций и слипы:
    ```bash
   
    git clone https://github.com/cyberomanov/sui-quests-3.git
   cd sui-quests-3/
   
   nano config.py          # config file
   nano data/mnemonic.txt  # mnemonic file
    ```
3. нужен python3.10 и новее.
4. установка:
    ```bash
    ## rust
    curl https://sh.rustup.rs -sSf | sh && \
    source "$HOME/.cargo/env"
   
    pip install maturin pysocks && \
    pip install -r ~/sui-quests-3/requirements.txt
    ```
5. запуск: 
    ```bash
    ## leaderboard
    python3 ~/sui-quests-3/main_leaderboard.py
   
    ## suilette
    python3 ~/sui-quests-3/main_suilette.py
   
    ## coinflip
    python3 ~/sui-quests-3/main_coinflip.py
    ```