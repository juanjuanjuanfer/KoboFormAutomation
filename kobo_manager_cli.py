import sys
from rich.panel import Panel
import kobo_manager
import os
from time import sleep

from utils import (
    console,
    display_header,
    get_credentials,
    save_credentials,
    login_prompt
)

def main():
    display_header()
    
    # Credential handling
    credentials = get_credentials()
    
    if credentials:
        api_token, asset_uid = credentials
        console.print(Panel(
            f"Found credentials for project: [bold]{asset_uid}[/]",
            style="success"
        ))
        if console.input("[prompt]Use these credentials? (Y/n):[/] ").lower() == 'n':
            api_token, asset_uid = login_prompt()
            save_credentials(api_token, asset_uid)
    else:
        console.print("No saved credentials found...", style="warning")
        api_token, asset_uid = login_prompt()
        save_credentials(api_token, asset_uid)
    
    # Connection attempt
    try:
        with console.status("[bold green]Connecting to KoboToolbox..."):
            form_manager = kobo_manager.FormManager(
                api_token=api_token,
                asset_uid=asset_uid
            )
        print(f"\033[H\033[2J")
        console.print(Panel(
            f"Connected to project: [bold]{asset_uid}[/]",
            style="success"
        ))
        
        # Main application loop
        while True:
            console.print("\n[bold]Main Menu:")
            console.print("[purple]VFS\t▓░▓\tView Form Structure\nED\t▓░▓\tExport Data\nAC\t▓░▓\tAdd Choices\nUR\t▓░▓\tUpdate and Redeploy \nA\t▓░▓\tAutoupdater\nAO\t▓░▓\tAutocreate Options.\nE\t▓░▓\tExit")
            choice = console.input("\n[prompt]Select an option:[/] ")

            if choice == 'VFS':
                console.print("\nForm Structure selected", style="info")
                form_manager.fetch_form_structure()
                console.print("Survey structure:", style="info")
                console.print(form_manager.asset_data["content"]["survey"])
                input("\033[7mPress Enter to continue...")
                console.print("Choices:", style="info")
                console.print(form_manager.asset_data["content"]["choices"])
                input("\033[7mPress Enter to continue...")
                print("\033[H\033[2J")

            if choice == "ED":
                console.print("\nExport Data selected", style="info")
                console.print("Exporting data...")
                form_manager.export_data()
                console.print("Data exported successfully", style="success")

            if choice == "AC":
                console.print("\nAdd Choices selected", style="info")
                form_manager.fetch_form_structure()
                console.print("Current choices:", style="info")
                console.print(form_manager.asset_data["content"]["choices"])
                list_name = console.input("[prompt]Enter the list name for the new choice: ")
                choice_label = console.input("[prompt]Enter the new choice label (the one will be shown in the fomr): ")
                choice_value = console.input("[prompt]Enter the new choice value (the one stored in kobo's database): ")
                console.print("Review the new choice:", style="warning")
                console.print(f"List name: {list_name}\nLabel: {choice_label}\nValue: {choice_value}")
                if console.input("[prompt]Add this choice? (Y/n): ").lower() == 'y':
                    form_manager.add_choice(kobo_manager.Choice(list_name, choice_value, choice_label))
                    form_manager.update_form()
                    console.print("Choice added successfully", style="success")
                else:
                    console.print("Operation cancelled", style="warning")
                form_manager.fetch_form_structure()
                console.print("Updated choices:", style="info")
                console.print(form_manager.asset_data["content"]["choices"])

            if choice == "UR":
                console.print("\nUpdate and Redeploy selected", style="warning")
                if form_manager.needs_redeploy is False:
                    console.print("No changes to deploy", style="warning")
                    continue
                form_manager.redeploy_form()

            if choice == 'A':
                console.print("Setting up autoupdater...", style="info")
                os.system("python autoupdater.py")
                console.print("Autoupdater started", style="success")


            if choice == 'AO':
                console.print("Starting auto-creation of options from database...", style="info")
                
                # Get existing list names from the form
                form_manager.fetch_form_structure()
                existing_lists = {c['list_name'] for c in form_manager.asset_data["content"]["choices"]}
                
                # Prompt user to select list name
                list_name = console.input(
                    f"[prompt]Enter target list name (existing: {', '.join(existing_lists)}): [/]"
                )
                
                if list_name not in existing_lists:
                    if console.input(f"List '{list_name}' doesn't exist. Create it? (y/N): ").lower() != 'y':
                        console.print("Operation cancelled", style="warning")
                        continue
                        
                # Database configuration
                db_config = {
                    'host': '',
                    'port': 5432,
                    'database': 'postgres',
                    'user': '',
                    'password': ''
                }
                
                try:
                    console.print("[bold green]Generating options from database...")
                    count = form_manager.autocreate_options_from_db(db_config, list_name)
                        
                    if count > 0 and console.input("[prompt]Update and redeploy form? (Y/n): ").lower() == 'y':
                        form_manager.update_form()
                        form_manager.redeploy_form()
                        
                except Exception as e:
                    console.print(f"Error during auto-creation: {str(e)}", style="error")                            

            if choice == 'E':
                if form_manager.needs_redeploy():
                    console.print(Panel(
                        "Unsaved changes detected - please update and redeploy before exiting",
                        style="warning"
                    ))
                    continue
                console.print(Panel("Goodbye!", style="error"))
                sleep(1)
                print("\033[H\033[2J")
                break
            
            if choice == "":
                print("\033[H\033[2J")

            console.print(f"Selected option {choice}", style="info")

            
    except Exception as e:
        console.print(Panel(
            f"Connection failed: {str(e)}",
            style="error"
        ))
        console.input("[prompt]Press Enter to exit...[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()