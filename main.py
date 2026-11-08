from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import datetime
import json
import os
from kivy.utils import platform

if platform not in ('android', 'ios'):
    Window.size = (390, 844) 

Window.clearcolor = (0.95, 0.95, 0.97, 1) 

# --- FIXED FILE PATH ISSUE HERE ---
# Automatically get the directory containing main.py and join it with bmi_history.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "bmi_history.json")

app_history = []

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            app_history = json.load(f)
        except json.JSONDecodeError as e:
            print("Error reading JSON file:", e)
            app_history = [] 

def save_data_to_file():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(app_history, f, ensure_ascii=False, indent=4)

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        layout.add_widget(Label(text="[b]BMI CALCULATOR[/b]", markup=True, font_size='28sp', color=(0.1, 0.2, 0.4, 1), size_hint=(1, 0.15)))

        # --- FIXED PADDING WARNING HERE ---
        # Replaced padding_y with padding to avoid Warning on the Terminal
        self.name_input = TextInput(
            hint_text="Enter your name...", 
            multiline=False, 
            font_size='18sp', 
            size_hint=(1, 0.12), 
            padding=[10, 15], 
            halign='center' 
        )
        layout.add_widget(self.name_input)

        self.height_label = Label(text="Height: 170 cm", font_size='20sp', color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.1))
        layout.add_widget(self.height_label)
        
        self.height_slider = Slider(min=100, max=220, value=170, step=1, size_hint=(1, 0.2))
        self.height_slider.bind(value=self.on_height_change) 
        layout.add_widget(self.height_slider)

        self.weight_label = Label(text="Weight: 65 kg", font_size='20sp', color=(0.2, 0.2, 0.2, 1), size_hint=(1, 0.1))
        layout.add_widget(self.weight_label)

        self.weight_slider = Slider(min=20, max=150, value=65, step=1, size_hint=(1, 0.2))
        self.weight_slider.bind(value=self.on_weight_change)
        layout.add_widget(self.weight_slider)

        btn_calc = Button(text="CALCULATE", font_size='18sp', bold=True, background_color=(0.2, 0.6, 0.8, 1), size_hint=(1, 0.18))
        btn_calc.bind(on_press=self.calculate)
        layout.add_widget(btn_calc)

        btn_history = Button(text="View History", font_size='16sp', background_color=(0.6, 0.6, 0.6, 1), size_hint=(1, 0.12))
        btn_history.bind(on_press=self.go_history)
        layout.add_widget(btn_history)

        self.add_widget(layout)

    def on_height_change(self, instance, value):
        self.height_label.text = f"Height: {int(value)} cm"

    def on_weight_change(self, instance, value):
        self.weight_label.text = f"Weight: {int(value)} kg"

    def calculate(self, instance):
        height = self.height_slider.value / 100
        weight = self.weight_slider.value
        bmi = weight / (height * height)
        
        user_name = self.name_input.text.strip()
        if not user_name:
            user_name = "Guest"
        
        self.manager.transition = SlideTransition(direction='left')
        
        result_screen = self.manager.get_screen('result')
        result_screen.update_result(user_name, bmi, int(self.height_slider.value), int(self.weight_slider.value))
        self.manager.current = 'result'

    def go_history(self, instance):
        self.manager.transition = SlideTransition(direction='up')
        self.manager.get_screen('history').load_history()
        self.manager.current = 'history'

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.score_label = Label(text="", font_size='60sp', bold=True)
        self.status_label = Label(text="", font_size='22sp', bold=True)
        
        self.advice_label = Label(text="", font_size='16sp', color=(0.3, 0.3, 0.3, 1), halign='center', valign='middle')
        self.advice_label.bind(size=self.advice_label.setter('text_size')) 
        
        self.current_bmi = 0
        self.current_info = ""

        self.btn_save = Button(text="Save to History", size_hint=(1, 0.2), background_color=(0.2, 0.8, 0.2, 1))
        self.btn_save.bind(on_press=self.save_result)

        btn_back = Button(text="Go Back", size_hint=(1, 0.2), background_color=(0.8, 0.3, 0.3, 1))
        btn_back.bind(on_press=self.go_back)

        self.layout.add_widget(self.score_label)
        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.advice_label)
        self.layout.add_widget(self.btn_save)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def update_result(self, name, bmi, height, weight):
        self.current_bmi = bmi
        self.current_info = f"{name} | {height}cm - {weight}kg"
        
        self.score_label.text = f"{bmi:.1f}"
        
        self.btn_save.disabled = False
        self.btn_save.text = "Save to History"

        if bmi < 18.5:
            self.score_label.color = self.status_label.color = (0.2, 0.6, 0.8, 1)
            self.status_label.text = "UNDERWEIGHT"
            self.advice_label.text = f"Hi {name}, you should consider increasing your nutritional intake!"
            
        elif 18.5 <= bmi < 24.9:
            self.score_label.color = self.status_label.color = (0.2, 0.8, 0.2, 1)
            self.status_label.text = "NORMAL"
            self.advice_label.text = f"Great job, {name}! Keep maintaining this healthy shape."
            
        else:
            self.score_label.color = self.status_label.color = (0.9, 0.2, 0.2, 1)
            self.status_label.text = "OVERWEIGHT"
            self.advice_label.text = f"Hi {name}, please pay more attention to your diet and exercise."

    def save_result(self, instance):
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        record = f"{now}\nBMI: {self.current_bmi:.1f} ({self.current_info})"
        
        app_history.append(record)
        save_data_to_file()
        
        self.btn_save.text = "Saved Successfully!"
        self.btn_save.disabled = True # don't allow the button to be clicked again (spam)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'input'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.layout.add_widget(Label(text="[b]BMI HISTORY[/b]", markup=True, font_size='24sp', color=(0.1, 0.2, 0.4, 1), size_hint=(1, 0.1)))

        self.scroll = ScrollView(size_hint=(1, 0.8))
        
        self.history_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.history_box.bind(minimum_height=self.history_box.setter('height'))
        
        self.scroll.add_widget(self.history_box)
        self.layout.add_widget(self.scroll)

        btn_back = Button(text="Close", size_hint=(1, 0.1), background_color=(0.5, 0.5, 0.5, 1))
        btn_back.bind(on_press=self.go_back)
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def load_history(self):
        self.history_box.clear_widgets()
        
        if not app_history:
            self.history_box.add_widget(Label(text="No data available yet.", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=40))
        else:
            for record in reversed(app_history):
                lbl = Label(text=record, color=(0, 0, 0, 1), size_hint_y=None, height=50, halign='left')
                lbl.bind(size=lbl.setter('text_size')) 
                self.history_box.add_widget(lbl)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='down')
        self.manager.current = 'input'

class ProBMIApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InputScreen(name='input'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm

if __name__ == "__main__":
    ProBMIApp().run()