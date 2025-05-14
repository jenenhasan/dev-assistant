from speech import VoiceControl
import os
import sys
from pathlib import Path
from datetime import datetime
import dateparser
import time
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from working_day.app_lanchuar import DynamicLauncher
from scaffolding.scaffold import ScaffoldingManager
from managment.email_managment import EmailManager
from managment.CalenderManagment import CalendarManager
from gemini import GeminiAPI
import json 
import webrtcvad 
import pyaudio
import re 
import subprocess
import platform


#use it for the voice activity detection 



sample_rate = 16000
frame_duration = 30  # ms
chunsk_size = int(sample_rate * frame_duration / 1000)  # Number of samples per frame 




# will use picovoice porcupine for dynamic listening 


# Constants
MAX_RETRIES = 2
DEFAULT_PHRASE_TIME = 30  # seconds
SHORT_PHRASE_TIME = 10    # seconds

class VoiceAssistant:
    def __init__(self):
        self.voice = VoiceControl()
        self.launcher = DynamicLauncher()
        self.scaffolding = ScaffoldingManager()
        self.calendar = CalendarManager()
        self.GeminiAPI = GeminiAPI()
        self.email = EmailManager()
        self.is_active = False
        self.thinking = False
        self.is_speaking = False 
        self.interrupted = False
        
        # Register commands with more natural language variations
        self.commands = {}
        self.register_commands()
        
        # Set up continuous listening
        self.listening_thread = None
        self.stop_listening = False

        self.vad = webrtcvad.Vad(3)
        self.sample_rate = 16000
        self.frame_duration = 30  # ms
        self.chunk_size = int(sample_rate * frame_duration / 1000)  # Number of samples per frame 
        #initialize pyaudio
        audio = pyaudio.PyAudio()
        self.stream = audio.open(
            format = pyaudio.paInt16,
            channels = 1,
            rate = sample_rate,
            input = True,
            frames_per_buffer = chunsk_size,
            )
    def speak(self , text):
        self.is_speaking = True
        self.interrupted = False
        try : 
            self.voice.speak(text)
        finally:
            if not self.interrupted:
                self.is_speaking = False

    def stop_speaking(self):
        self.interrupted = True
        try:
            if platform.system() == "Darwin":
                subprocess.run(["killall", "say"], stderr=subprocess.DEVNULL)
            elif platform.system() == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "mshta.exe"], stderr=subprocess.DEVNULL)
            else:  # Linux
                subprocess.run(["pkill", "-f", "festival"], stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "espeak"], stderr=subprocess.DEVNULL)
        
        except Exception as e:
            print(f"Error stopping speech: {e}")
        finally:
            self.is_speaking = False







   
    



    def register_commands(self):
        """Register all voice commands with more natural variations"""
        self.commands = {
            "app_launch": {
                "triggers": [
                    "open (the) app", "launch (the) app", "start (the) application",
                    "open (the) website", "launch", "run (the) app", "start (the) program"
                ],
                "action": self.handle_generic_launch,
                "help": "Launch applications or websites"
            },
            "create_project": {
                "triggers": [
                    "create (a) project", "make (a) new project", "scaffold",
                    "start (a) new project", "initialize project"
                ],
                "action": self.handle_scaffolding,
                "help": "Create a new project scaffold"
            },
            "create_event": {
                "triggers": [
                    "create (an) event", "schedule (a) meeting", "add to calendar",
                    "add (an) event", "schedule (an) event", "set up (a) meeting"
                ],
                "action": self.create_event,
                "help": "Add events to your calendar"
            },
            "create_task": {
                "triggers": [
                    "create (a) task", "add (a) task", "schedule (a) task",
                    "add to task list", "add to do", "add to my tasks"
                ],
                "action": self.create_task,
                "help": "Add tasks to your to-do list"
            },
            "send_email": {
                "triggers": [
                    "send (an) email", "compose (an) email", "email someone",
                    "write (an) email", "mail to", "send message to"
                ],
                "action": self.handle_sendemail, 
                "help": "Compose and send emails"
            },
            "check_inbox": {
                "triggers": [
                    "check inbox", "show emails", "read emails",
                    "check my mail", "any new emails", "unread emails"
                ],
                "action": self.handle_check_inbox,
                "help": "Check your email inbox"
            },
            "search_email": {
                "triggers": [
                    "search email", "find email", "look up email",
                    "search for email", "find message about"
                ],
                "action": self.handle_searchemail,
                "help": "Search through your emails"
            },
            "help": {
                "triggers": ["help", "what can you do", "show commands"],
                "action": self.show_help,
                "help": "Show available commands"
            },
            "setup_workspace":{
                "triggers":[
                    "setup workspace", "create workspace", "save workspace",
                    "add workspace", "save my workspace"
                ] , 
                "action": self.handle_setup_workspace, 
                "help": "Save your workspace configuration"
            }, 
            "load_workspace":{
                "triggers":[
                    "load workspace", "open workspace", "launch workspace",
                    "load my workspace", "open my workspace"
                ] , 
                "action": self.handle_launch_workspace,
                "help": "Load your saved workspace configuration"
            },
            

        }
        
        for cmd in self.commands.values():
            self.voice.register_command(cmd["triggers"], cmd["action"])
    def handle_setup_workspace(self):
        """Handle workspace setup with better feedback"""
        self.voice.speak("Please open all the applications you want in your workspace now")
        time.sleep(5)
        if platform.system() == "Darwin":  # MacOS
            proc = subprocess.run(["osascript", "-e", 'tell app "System Events" to get name of every process whose background only is false'], 
                                  capture_output=True, text=True)
            open_apps = [app.strip() for app in proc.stdout.split(',') if app.strip()]
        elif platform.system() == "Windows":
            open_apps = []  # Implement Windows version here
        else:  # Linux
            proc = subprocess.run(["wmctrl", "-lxp"], capture_output=True, text=True)
            open_apps = [line.split()[2] for line in proc.stdout.splitlines()]
        if open_apps:
            self.launcher.save_workspace("default" , open_apps)
            self.voice.speak(f"Workspace saved with {len(open_apps)} applications.")
        else:
            self.voice.speak("No applications found to save in the workspace.")

    def handle_launch_workspace(self):
        if self.launcher.launch_workspace("default"):
            self.voice.speak("Your workspace applications are launching now!")
        else:
            self.voice.speak("You haven't set up a workspace yet. Say 'setup my workspace' after opening your preferred apps.")

    
   


    def startA(self):
        """Start the voice assistant with a friendly welcome"""
        self.is_active = True
        self.voice.speak_random([
            "Hello, I'm Deva. How can I assist you today?",
            "Hi there! I'm Deva, your voice assistant. What can I do for you?",
            "Deva here, ready to help. What do you need?"
        ])
        
        # Start continuous listening in a separate thread
        self.stop_listening = False
        self.listening_thread = threading.Thread(target=self.run)
        self.listening_thread.start()


   

    def stopA(self):
        """Stop the voice assistant gracefully"""
        self.is_active = False
        self.stop_listening = True
        if self.listening_thread:
            self.listening_thread.join()
        
        self.voice.speak_random([
            "Have a productive day!",
            "Goodbye! Let me know if you need anything else.",
            "Signing off. Don't hesitate to call me back!"
        ])
###show help if the user says help 
    def show_help(self):
        """Display available commands to the user"""
        help_text = "Here's what I can help you with:\n"
        for cmd in self.commands.values():
            help_text += f"- {cmd['help']}\n"

        self.voice.speak(help_text)
        self.voice.speak("You can also say 'What can you do?' for a list of commands.")
        
       

    def listen_with_retry(self, prompt=None, phrase_time_limit=DEFAULT_PHRASE_TIME, max_retries=MAX_RETRIES):
        """Helper method to handle listening with retries and feedback"""
        if prompt:
            self.voice.speak(prompt)
            
        for attempt in range(max_retries):
            try:
                text = self.voice.listen(phrase_time_limit=phrase_time_limit)
                if text and text.strip():
                    return text.strip()
                
                if attempt < max_retries - 1:
                    self.voice.speak_random([
                        "I didn't catch that. Could you please repeat?",
                        "Sorry, I missed that. Could you say it again?",
                        "I didn't hear you clearly. Once more please?"
                    ])
            except Exception as e:
                print(f"Listening error: {e}")
                if attempt < max_retries - 1:
                    self.voice.speak("There was a problem with my microphone. Let's try again.")
        
        self.voice.speak("I'm having trouble hearing you. Let's try again later.")
        return None

    def confirm_action(self, message):
        """Get user confirmation for important actions"""
        self.voice.speak(f"{message} Please say 'yes' to confirm or 'no' to cancel.")
        response = self.listen_with_retry(phrase_time_limit=SHORT_PHRASE_TIME)
        return response and 'yes' in response.lower()

    def show_thinking(self):
        """Visual/audio feedback that assistant is processing"""
        self.thinking = True
      

    def hide_thinking(self):
        """Hide processing indicator"""
        self.thinking = False
        


    

    ################################# Working Day #############################################
    def handle_generic_launch(self):

        
        """Handle launch application/website commands with better feedback"""
        app_name = self.listen_with_retry(
            "Which application or website would you like me to launch?",
            phrase_time_limit=SHORT_PHRASE_TIME
        )
        
        if not app_name:
            return
            
        self.show_thinking()
        try:
            result = self.launcher.launch_target(app_name)
            if result.get('success'):
                self.voice.speak(f"I've opened {app_name} for you.")
            else:
                self.voice.speak(f"Sorry, I couldn't find {app_name}. Please try another name.")
        except Exception as e:
            self.voice.speak("There was an error launching the application. Please try again.")
            print(f"Launch error: {e}")
        finally:
            self.hide_thinking()

    ########################### Scaffolding ###################################################
    def handle_scaffolding(self):
        """Improved project creation with better guidance"""
        try:
            self.voice.speak("Let's create a new project. What kind of project would you like to make?")
            
            # Step 1: Get project type
            project_type = None
            for attempt in range(MAX_RETRIES):
                response = self.listen_with_retry(
                    "You can say things like 'Python project', 'React app', or 'Node.js application'.",
                    phrase_time_limit=DEFAULT_PHRASE_TIME
                )
                
                if response:
                    project_type = self._clean_response("type", response)
                    if project_type:
                        break
                    else:
                        available_types = ", ".join(self.scaffolding.available_templates.keys())
                        self.voice.speak(f"I didn't recognize that project type. Available types are: {available_types}")
            
            if not project_type:
                return
                
            # Step 2: Get project name
            project_name = None
            for attempt in range(MAX_RETRIES):
                response = self.listen_with_retry(
                    "What would you like to name your project?",
                    phrase_time_limit=DEFAULT_PHRASE_TIME
                )
                
                if response:
                    project_name = self._clean_response("name", response)
                    if project_name:
                        break
            
            if not project_name:
                return
                
            # Step 3: Get additional options
            options = {"database": False, "auth": False, "exclude_folders": []}
            self.voice.speak("Would you like to include a database setup?")
            if self.confirm_action(""):
                options["database"] = True
                
            self.voice.speak("Should I include authentication setup?")
            if self.confirm_action(""):
                options["auth"] = True
                
            # Confirm before creating
            options_str = ""
            if options["database"]:
                options_str += " with database setup"
            if options["auth"]:
                options_str += " with authentication"
                
            confirmation = (
                f"I'll create a {project_type.replace('-', ' ')} project "
                f"named {project_name}{options_str if options_str else ' with default settings'}. "
                "Should I proceed?"
            )
            
            if self.confirm_action(confirmation):
                self.show_thinking()
                result = self.scaffolding.create_project(
                    project_type=project_type,
                    project_name=project_name,
                    target_dir=os.path.expanduser("~/projects"),
                    command=" ".join(options.get('options', []))
                )
                self.hide_thinking()
                
                if result.get('success'):
                    self.voice.speak(f"Success! Your project {project_name} has been created at {result.get('path', 'the default location')}.")
                else:
                    self.voice.speak(f"Sorry, there was an error creating your project: {result.get('message', 'Unknown error')}")
            else:
                self.voice.speak("Project creation cancelled.")
                
        except Exception as e:
            self.hide_thinking()
            self.voice.speak("An unexpected error occurred while creating your project.")
            print(f"Project creation error: {e}")

    def _clean_response(self, param_type, response):
        """Clean and validate user responses"""
        response = response.lower().strip()
        
        if param_type == "type":
            # Try exact match first
            if response in self.scaffolding.available_templates:
                return response
                
            # Then check aliases
            for template, config in self.scaffolding.available_templates.items():
                if response in config.get('aliases', []):
                    return template
                    
            # Try partial matches
            for template in self.scaffolding.available_templates.keys():
                if template in response or response in template:
                    return template
                    
        elif param_type == "name":
            # Basic sanitization
            return "".join(c for c in response if c.isalnum() or c in (' ', '-', '_'))
            
        return None
    

    ############################## Management ################################################

    ######### Calendar Management #################
    def create_event(self):
        """More robust event creation with natural language parsing"""
        self.voice.speak("Let's schedule an event. Please tell me the event name and time.")
        
        for attempt in range(MAX_RETRIES):
            command = self.listen_with_retry(
                "For example, you can say 'Team meeting tomorrow at 2pm' or 'Lunch with John next Friday at noon'.",
                phrase_time_limit=DEFAULT_PHRASE_TIME
            )
            
            if not command:
                continue
                
            parsed = self.calendar.parse_voice_command(command)
            
            if parsed["valid"]:
                break
                
            self.voice.speak(f"I didn't understand the time. {parsed.get('error', 'Please try again.')}")
        else:
            self.voice.speak("Let's try creating an event again later.")
            return
            
        # Verify details
        time_str = parsed["local_time"].strftime('%A, %B %d at %I:%M %p')
        confirm_msg = (
            f"Please confirm: {parsed['summary']} on {time_str} "
            f"for {parsed.get('duration', 60)} minutes."
        )
        
        if not self.confirm_action(confirm_msg):
            self.voice.speak("Event creation cancelled.")
            return
            
        # Create event
        self.show_thinking()
        try:
            result = self.calendar.create_event(
                parsed["summary"],
                parsed["start_time"],
                parsed.get("duration", 60),
                parsed.get("location", ""),
                parsed.get("attendees", [])
            )
            
            if result["success"]:
                self.voice.speak(f"All set! I've scheduled {parsed['summary']} for {time_str}.")
                if result.get("conflicts"):
                    self.voice.speak(f"Note: You have another event around that time: {result['conflicts'][0]['summary']}")
            else:
                self.voice.speak(f"Sorry, I couldn't create the event. {result.get('message', 'Please try again later.')}")
        except Exception as e:
            self.voice.speak("There was an error creating your event. Please try again.")
            print(f"Event creation error: {e}")
        finally:
            self.hide_thinking()

    def create_task(self):
        """Improved task creation with reminders"""
        self.voice.speak("Let's add a task. Please tell me the task and due date.")
        
        for attempt in range(MAX_RETRIES):
            command = self.listen_with_retry(
                "For example, you can say 'Finish report by Friday' or 'Call client tomorrow at 3pm'.",
                phrase_time_limit=DEFAULT_PHRASE_TIME
            )
            
            if not command:
                continue
                
            parsed = self.calendar.parse_voice_command(command)
            
            if parsed["valid"]:
                break
                
            self.voice.speak(f"I didn't understand the time. {parsed.get('error', 'Please try again.')}")
        else:
            self.voice.speak("Let's try adding a task again later.")
            return
            
        # Verify details
        time_str = parsed["local_time"].strftime('%A, %B %d at %I:%M %p')
        confirm_msg = f"Please confirm: Task '{parsed['summary']}' due on {time_str}."
        
        if not self.confirm_action(confirm_msg):
            self.voice.speak("Task creation cancelled.")
            return
            
        # Create task
        self.show_thinking()
        try:
            result = self.calendar.create_task(
                parsed["summary"],
                parsed["start_time"],
                reminder_minutes=15
            )
            
            if result["success"]:
                self.voice.speak(f"Task '{parsed['summary']}' has been added to your to-do list.")
                if result.get("reminder_set"):
                    self.voice.speak("I'll remind you 15 minutes before it's due.")
            else:
                self.voice.speak(f"Sorry, I couldn't create the task. {result.get('message', 'Please try again later.')}")
        except Exception as e:
            self.voice.speak("There was an error creating your task. Please try again.")
            print(f"Task creation error: {e}")
        finally:
            self.hide_thinking()

    ################# Email Management ##############
    def handle_sendemail(self):
        """Improved email sending with better recipient handling"""
        # Get recipient
        recipient_name = self.listen_with_retry(
            "Who would you like to email? You can say a name or email address.",
            phrase_time_limit=DEFAULT_PHRASE_TIME
        )
        
        if not recipient_name:
            return
            
        # Find recipient email
        self.show_thinking()
        recipient_email = self.email.find_email_by_name(recipient_name)
        self.hide_thinking()
        
        if not recipient_email:
            self.voice.speak(f"I couldn't find {recipient_name} in your contacts. Please try again with their full email address.")
            recipient_email = self.listen_with_retry(
                "What is their email address?",
                phrase_time_limit=DEFAULT_PHRASE_TIME
            )
            
            if not recipient_email:
                return
                
        # Get email content
        self.voice.speak(f"What would you like to say to {recipient_name}?")
        email_prompt = self.listen_with_retry(phrase_time_limit=60)
        
        if not email_prompt:
            return
            
        # Generate email content
        self.show_thinking()
        try:
            bodymssg = self.GeminiAPI.get_answer(
                f"Write a professional email about: {email_prompt}. "
                "Keep it concise (1-2 paragraphs max). "
                "Include a proper greeting and closing."
            )
            
            # Preview email
            self.voice.speak("Here's the email I prepared:")
            self.voice.speak(bodymssg[:500])  # Limit preview length
            
            if self.confirm_action("Would you like to send this email?"):
                result = self.email.send_email(recipient_email, bodymssg)
                if result['success']:
                    self.voice.speak(f"Email sent successfully to {recipient_name}.")
                else:
                    self.voice.speak(f"Failed to send email. {result.get('message', 'Please try again later.')}")
            else:
                self.voice.speak("Email not sent. Would you like me to revise it?")
                if self.confirm_action(""):
                    # Handle revision flow
                    pass
                else:
                    self.voice.speak("Email cancelled.")
        except Exception as e:
            self.voice.speak("There was an error composing your email. Please try again.")
            print(f"Email error: {e}")
        finally:
            self.hide_thinking()

    def handle_searchemail(self):
        """Improved email search with better results handling"""
        try:
            query = self.listen_with_retry(
                "What would you like to search for in your emails?",
                phrase_time_limit=SHORT_PHRASE_TIME
            )
            
            if not query:
                return
                
            self.show_thinking()
            searched_emails = self.email.search_email_by_subject(query)
            self.hide_thinking()
            
            if not searched_emails:
                self.voice.speak(f"No emails found about '{query}'.")
                return
                
            self.voice.speak(f"I found {len(searched_emails)} emails about '{query}'. Here are the most recent:")
            
            for i, email in enumerate(searched_emails[:3], 1):
                subject = email.get('subject', 'No subject').replace('Subject:', '').strip()
                sender = email.get('from', 'Unknown sender').split('<')[0].strip()
                date = email.get('date', '').split('(')[0].strip()
                
                summary = f"Email {i}: From {sender}, {date}. Subject: {subject[:100]}"
                self.voice.speak(summary)
                
            if len(searched_emails) > 3:
                self.voice.speak(f"Plus {len(searched_emails)-3} more emails.")
                
            self.voice.speak("Would you like me to read any of these emails?")
            response = self.listen_with_retry(phrase_time_limit=SHORT_PHRASE_TIME)
            
            # Add logic to handle reading specific emails
        except Exception as e:
            self.voice.speak("Sorry, I encountered an error searching your emails.")
            print(f"Email search error: {e}")

    def handle_check_inbox(self):
        """Improved inbox checking with prioritization"""
        self.voice.speak("Checking your inbox, please wait...")
        self.show_thinking()
        
        try:
            emails = self.email.read_emails_headlines(limit=5, unread_first=True)
            
            if not emails:
                self.voice.speak("Your inbox is empty.")
                return
                
            unread_count = sum(1 for email in emails if email.get('unread', False))
            
            if unread_count:
                self.voice.speak(f"You have {unread_count} new email{'s' if unread_count > 1 else ''}.")
            else:
                self.voice.speak("No new emails. Here are your most recent messages:")
            
            for i, email in enumerate(emails, 1):
                status = "New: " if email.get('unread', False) else ""
                subject = email.get('subject', 'No subject').replace('Subject:', '').strip()
                sender = email.get('from', 'Unknown').split('<')[0].strip()
                
                self.voice.speak(f"{status}From {sender}: {subject}")
                
            self.voice.speak("Would you like me to read any of these?")
            response = self.listen_with_retry(phrase_time_limit=SHORT_PHRASE_TIME)
            
            # Add logic to handle reading specific emails
        except Exception as e:
            self.voice.speak("Sorry, I couldn't access your inbox right now.")
            print(f"Inbox error: {e}")
        finally:
            self.hide_thinking()

    def run(self):
        """Main listening loop with VAD"""
        print("Voice assistant is listening... (VAD active)")
        
        while not self.stop_listening:
            try:
                # Read audio chunk
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Check for speech
                is_speech = self.vad.is_speech(audio_data, self.sample_rate)
                if self.is_speaking and is_speech:
                    continous_speech = 0 
                    for _ in range (3):
                        time.sleep(1)
                        new_audio = self.stream.read(self.chunk_size, exception_on_overflow=False)
                        if self.vad.is_speech(new_audio , self.sample_rate):
                            continous_speech +=1
                        else : 
                            break
                      
                    if continous_speech >= 3:
                        self.stop_speaking()
                        self.voice.speak("I'll stop here. What would you like to say?")
                        continue 
                
                if not is_speech:
                    time.sleep(0.1)
                    continue
                
                print("Speech detected! Processing...")
                text = self.voice.listen(phrase_time_limit=DEFAULT_PHRASE_TIME)
                
                if not text or not self.is_active:
                    continue
                
                text = text.lower()
                
                # Handle wake word
                if "deva" in text or "hey deva" in text:
                    self.is_active = True
                    self.voice.speak("Yes? How can I help?")
                    continue
                
                # Handle exit commands
                if any(word in text for word in ["exit", "quit", "stop", "goodbye"]):
                    self.stopA()
                    break
                
                # Process commands
                command_handled = False
                for cmd_data in self.commands.values():
                    for trigger in cmd_data["triggers"]:
                        clean_trigger = re.sub(r'\([^)]*\)', '', trigger).strip()
                        trigger_words = clean_trigger.split()
                        text_words = text.split()
                        if self.words_in_order(trigger_words, text_words):
                            cmd_data["action"]()
                            command_handled = True
                            break
                    if command_handled:
                        break
                          
                  
                
                # Fall back to Gemini
                if not command_handled and text.strip():
                    self.show_thinking()
                    try:
                        answer = self.GeminiAPI.get_answer(f" answer it in short way {text}")
                        self.voice.speak(answer)
                    except Exception as e:
                        self.voice.speak("I'm having trouble answering that right now. Please try again.")
                        print(f"Gemini error: {e}")
                    finally:
                        self.hide_thinking()
                        
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(1)
    def words_in_order(self, trigger_words, text_words):
        it = iter(text_words)
        return all(word in it for word in trigger_words)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    try:
        assistant.startA()
    except KeyboardInterrupt:
        assistant.stopA()