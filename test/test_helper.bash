setup () {
  source ~/venv/bin/activate
}
teardown() {
  deactivate
}

export printvault=/vagrant/print_vault_value.py
export pylint="pylint"
export program=/vagrant/anmad_buttons.py
export version=0.16.2
source ~/venv/bin/activate
