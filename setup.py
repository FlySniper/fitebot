from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': []}

base = 'service'

executables = [
    Executable('client.py', base=base, target_name = 'fitebot')
]

setup(name='fitebot',
      version = '1.0',
      description = 'A map database and matchmaker',
      options = {'build_exe': build_options},
      executables = executables)
