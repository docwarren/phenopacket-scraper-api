# Changing the default port of runserver to 8001
from django.core.management.commands.runserver import Command
Command.default_port= "8001"