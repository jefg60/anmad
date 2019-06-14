setup () {
  source venv/bin/activate
}
teardown() {
  deactivate
}

export printvault=./print_vault_value.py
export pylint="pylint"
export program=./anmad_buttons.py
export version=0.15.4
source venv/bin/activate
