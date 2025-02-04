import kobo_manager
from utils import cli_print

cli_print("Welcome to KoboToolbox Form Manager by Me\n", 0.03)
cli_print("Please, enter the project UID.\nYou can find it on the form page url, just after the <form> like the example:\nhttps://eu.kobotoolbox.org/form/<FORM_UID>/\n", 0.03, 0)

UID = input("(insert the UID here)")

cli_print("\nTrying to read the form\n")
cli_print("\t... ... ...", sleeptime=0.2)

try:
    kobo_manager.FormManager(api_token=API_TOKEN, asset_uid=asset_uid)