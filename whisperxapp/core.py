import ipywidgets as widgets
from IPython.display import display, clear_output
import os

# Assuming config_advanced.py exists and contains these variables
from whisperxapp.config_advanced import root_path, output_dir, output_format, args, parser, model, device, compute_type, language

class WhisperXApp:
    def __init__(self):
        self.hf_token = self._get_hf_token()
        self.common_widget_layout = widgets.Layout(width='90%', margin='5px 0')
        self._setup_ui()
        self._set_initial_widget_states()
        self._observe_widget_changes()

    def _get_hf_token(self):
        """Attempts to get Hugging Face token from file or prompts user to login."""
        try:
            from hf_token import hf_token
            if hf_token == "YOUR_HUGGINGFACE_TOKEN_HERE":
                print("Please enter your Hugging Face access token below.")
                print("If you don't have one, you can create one here: https://huggingface.co/settings/tokens")
                from huggingface_hub import login
                login()
                # After login, the token might be available in environment or cached
                # For simplicity here, we'll assume the user logs in and the token is set.
                # In a real scenario, you might want to re-check or store it.
                return os.environ.get("HF_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")
            return hf_token
        except ImportError:
            return "YOUR_HUGGINGFACE_TOKEN_HERE" # Fallback if hf_token.py doesn't exist

    def _create_dropdown(self, options_dict, description, default_key):
        """Helper to create consistent dropdown widgets."""
        return widgets.Dropdown(
            options=list(options_dict.keys()),
            value=options_dict[default_key],
            description=description,
            layout=self.common_widget_layout
        )

    def _setup_ui(self):
        """Defines all the UI widgets and their initial layout."""
        # Basic Options
        self.audio_uploader = widgets.FileUpload(
            multiple=False,
            description="Upload Audio",
            layout=self.common_widget_layout
        )
        self.task_dropdown = widgets.Dropdown(
            options=["transcribe", "translate"],
            value="transcribe",
            description="Task:",
            layout=self.common_widget_layout
        )
        self.diarize_checkbox = widgets.Checkbox(
            value=True,
            description="Speaker Recognition",
            indent=False,
            layout=self.common_widget_layout
        )
        speakers_options = [("unknown", None)] # Initialize with the "unknown" option

        # Define the range of integers for speakers
        min_speakers = 1
        max_speakers = 10 # You can adjust this to your desired maximum

        for i in range(min_speakers, max_speakers + 1):
            speakers_options.append((i, i))

        self.speakers_dropdown = widgets.Dropdown(
            options=speakers_options,
            value=None,
            description="Speakers:",
            layout=self.common_widget_layout
        )
        self.advanced_options_checkbox = widgets.Checkbox(
            value=False,
            description="Advanced Options",
            indent=False,
            layout=self.common_widget_layout
        )

        self.basic_widgets_box = widgets.VBox([
            self.audio_uploader,
            self.task_dropdown,
            widgets.HBox([self.diarize_checkbox, self.speakers_dropdown]),
            self.advanced_options_checkbox
        ], layout=widgets.Layout(width='50%', margin='0 auto', border='1px solid #ccc', padding='15px'))

        # Advanced Options
        self.model_dropdown = self._create_dropdown(model, "Model:", "default")
        self.device_dropdown = self._create_dropdown(device, "Device:", "default")
        self.compute_type_dropdown = self._create_dropdown(compute_type, "Quant:", "default")
        self.output_format_dropdown = self._create_dropdown(output_format, "Output:", "default")
        self.language_dropdown = self._create_dropdown(language, "Language:", "default")
        self.initial_prompt_textarea = widgets.Textarea(
            value="",
            placeholder="Enter an initial prompt",
            description="Prompt:",
            layout=self.common_widget_layout
        )
        self.highlight_words_checkbox = widgets.Checkbox(
            value=False,
            description="Highlight Words",
            indent=False,
            layout=self.common_widget_layout
        )

        self.advanced_widgets_box = widgets.VBox([
            self.model_dropdown,
            self.device_dropdown,
            self.compute_type_dropdown,
            self.output_format_dropdown,
            self.language_dropdown,
            self.initial_prompt_textarea,
            self.highlight_words_checkbox
        ], layout=widgets.Layout(width='50%', margin='0 auto', border='1px solid #ccc', padding='15px'))

        # Run Button and Output Area
        self.run_button = widgets.Button(
            description="Run Transcription",
            layout=self.common_widget_layout
        )
        self.output_area = widgets.Output()

        self.run_widgets_box = widgets.VBox([
            self.run_button,
            self.output_area,
        ], layout=widgets.Layout(width='50%', margin='0 auto', border='1px solid #ccc', padding='15px'))

    def _set_initial_widget_states(self):
        """Sets the initial disabled/hidden states for widgets."""
        self.speakers_dropdown.disabled = False
        self.advanced_widgets_box.layout.display = 'none'

    def _observe_widget_changes(self):
        """Sets up observers for widget value changes."""
        self.diarize_checkbox.observe(self._on_diarize_checkbox_change, names='value')
        self.advanced_options_checkbox.observe(self._on_advanced_options_checkbox_change, names='value')
        self.task_dropdown.observe(self._on_task_dropdown_change, names='value')
        self.run_button.on_click(self._on_run_button_click)

    def _on_diarize_checkbox_change(self, change):
        """Callback for diarize checkbox."""
        self.speakers_dropdown.disabled = not change.new
        if not change.new:
            self.speakers_dropdown.value = None

    def _on_advanced_options_checkbox_change(self, change):
        """Callback for advanced options checkbox."""
        self.advanced_widgets_box.layout.display = 'block' if change.new else 'none'

    def _on_task_dropdown_change(self, change):
        """Callback for task dropdown."""
        if change.new == "translate":
            self.highlight_words_checkbox.disabled = True
            self.highlight_words_checkbox.value = False
        else:
            self.highlight_words_checkbox.disabled = False
            self.highlight_words_checkbox.value = True # Or keep previous value if preferred

    def _on_run_button_click(self, b):
        """Callback for the run button, initiating transcription."""
        with self.output_area:
            clear_output()
            print("Starting transcription...")

            if not self.audio_uploader.value:
                print("Please upload an audio file first.")
                return # Exit early if no file

            #try:
            # Handle uploaded file
            file_metadata = self.audio_uploader.value[0]
            uploaded_file_name = file_metadata['name']
            uploaded_content_bytes = file_metadata['content'].tobytes()

            audio_file_path = os.path.join(root_path, "media", uploaded_file_name)
            os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)
            with open(audio_file_path, 'wb') as f:
                f.write(uploaded_content_bytes)

            # Gather widget values
            current_args = args.copy() # Start with a copy of default args from config
            current_args["audio"] = [audio_file_path]
            current_args["task"] = self.task_dropdown.value

            if self.diarize_checkbox.value:
                current_args["diarize"] = True
                if self.hf_token and self.hf_token != "YOUR_HUGGINGFACE_TOKEN_HERE":
                    current_args["hf_token"] = self.hf_token
                else:
                    print("Warning: Hugging Face token not configured for diarization. Diarization may fail.")
                current_args["min_speakers"] = self.speakers_dropdown.value
                current_args["max_speakers"] = self.speakers_dropdown.value

            if self.advanced_options_checkbox.value:
                current_args["model"] = self.model_dropdown.value
                current_args["device"] = self.device_dropdown.value
                current_args["compute_type"] = self.compute_type_dropdown.value
                current_args["output_format"] = self.output_format_dropdown.value
                current_args["language"] = self.language_dropdown.value
                if self.initial_prompt_textarea.value:
                    current_args["initial_prompt"] = self.initial_prompt_textarea.value
                current_args["highlight_words"] = self.highlight_words_checkbox.value

            # Execute transcription
            from whisperx.transcribe import transcribe_task
            transcribe_task(current_args, parser)
            print("whisperX execution completed successfully.")

            output_file_name = os.path.basename(audio_file_path).rsplit('.', 1)[0] + f".{self.output_format_dropdown.value}"
            print(f"Output saved to: {os.path.join(output_dir, output_file_name)}")

            #except Exception as e:
            #    print(f"An unexpected error occurred: {e}")

    def display_app(self):
        """Displays all the UI components."""
        display(self.basic_widgets_box, self.advanced_widgets_box, self.run_widgets_box)

def execute():
    app = WhisperXApp()
    app.display_app()

if __name__ == "__main__":
    execute()