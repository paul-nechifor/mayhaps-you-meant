# Mayhaps You Meant

This is a Reddit bot which aims to inform people about their grammatical errors
without upsetting them.

## Contributions

You can contribute by:

* adding more corrections in [data/corrections.yaml](data/corrections.yaml),
* updating the response grammar in [data/responses.xml](data/responses.xml).

## Install

Get Virtualenv if you don't have it:

    sudo pip install virtualenv

Install the script's dependencies:

    virtualenv env
    env/bin/pip install -r requirements.txt

## Configure

You can reset private fields from [`config.yaml`](config.yaml) by writing them
in `config-private.yaml` which is ignored from source control. Duplicate and
edit the example config override:

    cp config-private-ex.yaml config-private.yaml
    vim config-private.yaml # Or another editor.

## Running

Run the bot:

    env/bin/python bot.py

## License

MIT
