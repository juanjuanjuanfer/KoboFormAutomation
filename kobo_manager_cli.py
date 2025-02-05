import sys
from utils import (
    console,
    display_header,
    typewriter_print,
    get_credentials,
    save_credentials,
    login_prompt
)
from rich.panel import Panel
import kobo_manager
import os
# Add this helper function
import uuid

def generate_kuid():
    return str(uuid.uuid4())[:8].lower()

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
        
        console.print(Panel(
            f"Connected to project: [bold]{asset_uid}[/]",
            style="success"
        ))
        
        # Main application loop
        while True:
            console.print("\n[bold]Main Menu:")
            console.print("1. View Form Structure\n2. Export Data\n3. Add Choices\n4. Update and Redeploy \na. Autoupdater\nao. Autocreate options.\ne. Exit")
            choice = console.input("[prompt]Select an option:[/] ")
            
            if choice == '1':
                console.print("\nForm Structure selected", style="info")
                form_manager.fetch_form_structure()
                console.print("Survey structure:", style="info")
                console.print(form_manager.asset_data["content"]["survey"])
                input("Press Enter to continue...")
                console.print("Choices:", style="info")
                console.print(form_manager.asset_data["content"]["choices"])

            if choice == "2":
                console.print("\nExport Data selected", style="info")
                console.print("Exporting data...")
                form_manager.export_data()
                console.print("Data exported successfully", style="success")

            if choice == "3":
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

            if choice == "4":
                console.print("\nUpdate and Redeploy selected", style="warning")
                if form_manager.needs_redeploy is False:
                    console.print("No changes to deploy", style="warning")
                    continue
                form_manager.redeploy_form()

            if choice == 'a':
                console.print("Setting up autoupdater...", style="info")
                os.system("python autoupdater.py")
                console.print("Autoupdater started", style="success")


            if choice == 'ao':
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
                        

                try:
                    with console.status("[bold green]Generating options from database..."):
                        count = form_manager.autocreate_options_from_db(db_config, list_name)
                        
                    if count > 0:
                        console.print(f"Added {count} new options to list '{list_name}'", style="success")
                        if console.input("[prompt]Update and redeploy form? (Y/n): ").lower() == 'y':
                            form_manager.update_form()
                            form_manager.redeploy_form()
                    else:
                        console.print("No new options to add", style="warning")
                        
                except Exception as e:
                    console.print(f"Error during auto-creation: {str(e)}", style="error")
                            

            if choice == 'e':
                if form_manager.needs_redeploy():
                    console.print(Panel(
                        "Unsaved changes detected - please update and redeploy before exiting",
                        style="warning"
                    ))
                    continue
                console.print(Panel("Goodbye!", style="error"))
                break
            
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