import os
import subprocess
import webbrowser
import platform
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List

#
#Workflow Automation

   # "Open VS Code and start Django server"

   # Chain terminal commands:


class DynamicLauncher:
    def __init__(self):
        self.system = platform.system()
        self.config_path = Path.home() / ".voice_assistant_config.json"
        self.aliases = {
            "chrome": "chrome",
            "google chrome": "google-chrome" if self.system == "Linux" else "chrome",
            "vscode": "code",
            "vs code": "code",
            "visual studio code": "code",
            "terminal": "gnome-terminal" if self.system == "Linux" else "cmd",
            "notion" : "notion-desktop" if self.system == "Linux" else "notion",
            "telegram" : "telegram"
            

        }
        self.web_services = {
            "github": "https://github.com",
            "notion": "https://www.notion.so",
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "stackoverflow": "https://stackoverflow.com",
            "twitter": "https://twitter.com",
            "linkedin": "https://www.linkedin.com",
            "instagram": "https://www.instagram.com",
            "facebook": "https://www.facebook.com",
            "reddit": "https://www.reddit.com",
            "twitch": "https://www.twitch.tv",
            "discord": "https://www.discord.com",
            "whatsapp": "https://web.whatsapp.com",
            "telegram": "https://web.telegram.org",
            "slack": "https://slack.com",
            "notion": "https://www.notion.so",
            "deepseek": "https://deepseek.com",
            "figma": "https://www.figma.com",
            "canva": "https://www.canva.com",
            "trello": "https://trello.com",
            "jira": "https://www.atlassian.com/software/jira",
            "microsoft teams": "https://teams.microsoft.com",
            "zoom": "https://zoom.us",
            "skype": "https://www.skype.com",
            "google meet": "https://meet.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "signal": "https://signal.org",
            "viber": "https://www.viber.com",
            "snapchat": "https://www.snapchat.com",
            "tiktok": "https://www.tiktok.com",
            "pinterest": "https://www.pinterest.com",
            "quora": "https://www.quora.com",
            "github": "https://github.com",
            "gitlab": "https://gitlab.com",
            "bitbucket": "https://bitbucket.org",
            "docker": "https://www.docker.com",
            "kubernetes": "https://kubernetes.io",
            "aws": "https://aws.amazon.com",
            "azure": "https://azure.microsoft.com",
            "google cloud": "https://cloud.google.com",
            "ibm cloud": "https://www.ibm.com/cloud",
            "oracle cloud": "https://www.oracle.com/cloud",
            "salesforce": "https://www.salesforce.com",
            "hubspot": "https://www.hubspot.com",
            "mailchimp": "https://mailchimp.com",
            "sendgrid": "https://sendgrid.com",

        }
        logging.basicConfig(filename='assistant.log', level=logging.INFO)

    def resolve_alias(self, name: str) -> str:
        return self.aliases.get(name.lower(), name)

    def find_application(self, app_name: str) -> str:
        """Find application path based on platform and app name."""
        try:
            app_name = self.resolve_alias(app_name)

            # For Linux: try finding .desktop files and check paths
            if self.system == "Linux":
                if path := shutil.which(app_name):
                    return path
                
                snap_path = f"/snap/bin/{app_name}"
                if os.path.exists(snap_path):
                    return snap_path
                
                desktop_dirs = [
                    "/usr/share/applications",
                    "~/.local/share/applications",
                    "/var/lib/snapd/desktop/applications"

                ]
                for dir_path in desktop_dirs:
                    expanded = os.path.expanduser(dir_path)
                    if path(expanded).exists():
                        for file in path(expanded).rglob(f"{app_name}*.desktop"):
                            return str(file)
                return ""
              

            # For MacOS: use `mdfind` to find app
            elif self.system == "Darwin":
                return self._find_mac_app(app_name)

            # For Windows: search in program files
            elif self.system == "Windows":
                return self._find_windows_app(app_name)

            return ""
        except Exception as e:
            print(f"[ERROR] Application find failed: {e}")
            return ""

    def _find_mac_app(self, app_name: str) -> str:
        result = subprocess.run(
            ["mdfind", "-name", f"{app_name}.app"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n')[0] if result.stdout else ""

    def _find_windows_app(self, app_name: str) -> str:
        locations = [
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("APPDATA", "")
        ]
        for root in locations:
            if not os.path.exists(root):
                continue
            for path in Path(root).rglob(f"{app_name}*.exe"):
                return str(path)
        return ""

    def launch_target(self, target: str) -> bool:
        try:
            target = target.strip().lower()
            app_path = self.find_application(target)
            if app_path:
                if self.system == "Linux" and app_path.endswith(".desktop"):
                    subprocess.Popen(["gtk-launch", os.path.basename(app_path)[:-8]], shell=True)
                else : 
                    subprocess.Popen([app_path], shell=(self.system == "Linux"))
                return True
            if target in self.web_services:
                url = self.web_services[target]
                webbrowser.open(url)
            
                return True
            

           
          
            #subprocess.Popen(target.split(), shell=(self.system == "Linux"))

        except Exception as e:
            logging.error(f"Launch failed: {target} - {str(e)}")
            print(f"Error launching {target}: {e}")
            return False

           
    def first_time_setup(self) -> Dict:
        config = {"targets": []}
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
        return config

    def load_config(self) -> Dict:
        #just load it 
        if not self.config_path.exists():
            return self.first_time_setup()
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                assert isinstance(config.get("targets", []), list)
                return config
        except Exception as e:
            logging.error(f"Config error: {str(e)}")
            return self.first_time_setup()

  

    def add_target(self, target: str):
        config = self.load_config()
        if target not in config["targets"]:
            config["targets"].append(target)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"Added target: {target}")
        else:
            print(f"Target already exists: {target}")

    def launch_environment(self, debug=False) -> None:
        config = self.load_config()
        targets = config.get("targets", [])
        successes = 0

        if debug:
            print(f"Launching {len(targets)} targets...")

        for target in targets:
            if debug:
                print(f"Trying to launch: {target}")
            if self.launch_target(target):
                successes += 1
                logging.info(f"Launched: {target}")
            else:
                logging.warning(f"Failed: {target}")

        logging.info(f"Success rate: {successes}/{len(targets)}")
        if debug:
            print(f"Launched {successes} of {len(targets)}")

    def save_workspace(self , name: str, targets: List[str]):
        config = self.load_config()
        if "workspace" not in config:
            config["workspace"] = {}
        config["workspace"][name]= targets
        with open(self.config_path , "w")as f:
            json.dump(config , f , indent=2)
    def load_workspace(self , name: str):
        config = self.load_config()
        return config.get("workspace" , {}).get(name , [])
    
    
    def launch_workspace(self , name: str):
     




        targets = self.load_workspace(name)
        print (f"[DEBUG] Launching workspace: {name} : {targets}")
        
        if not targets:
            print(f"[ERROR] Workspace '{name}' not found or empty.")
            return False
        results = []
        for target in targets:
            success = self.launch_target(target)
            results.append(success)
        return all(results)
           
       # return all(self.launch_target(target) for target in targets)
            
   



if __name__ == "__main__":
    launcher = DynamicLauncher()
    
   

   

    # Launch all
    launcher.launch_environment(debug=True)
    launcher.save_workspace("dev" , ["vscode" , "chrome" , "notion" , "terminal" , "deepseek" , "telegram"])
    launcher.load_workspace("deva")
    launcher.launch_workspace("dev")

