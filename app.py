# DentalProfit Pro - Cross-Platform App using Kivy
# This is a Python/Kivy implementation of the provided Streamlit app, adapted for desktop (Windows/Mac/Linux) and mobile (Android/iOS).
# To run on desktop: Install Kivy (pip install kivy), then python main.py
# For packaging:
# - Desktop/Mac: Use PyInstaller (pip install pyinstaller), then pyinstaller --onefile --windowed main.py
# - Mobile: Use Buildozer for Android (pip install buildozer), buildozer init, edit buildozer.spec, buildozer android debug
# - For iOS: Use Kivy's toolchain (more complex, see docs: https://kivy.org/doc/stable/guide/packaging-ios.html)
# To sell to dentists: 
# - Add a better licensing system (e.g., integrate with Stripe for payments or use a server for license validation).
# - For app stores: Sign up for Apple Developer Program ($99/year) for iOS/Mac, Google Play Console ($25 one-time) for Android.
# - Include privacy policy, terms of service (GDPR/HIPAA compliant for health data).
# - Features added: Data persistence with JSON/CSV, offline support, basic error handling.
# - Everything necessary: Authentication, data export, charts, editable tables, calculations.
# Note: Replace simple password with a proper system (e.g., UUID-based licenses stored in a cloud DB like Firebase).
# For charts, using Matplotlib integrated with Kivy.

import kivy
kivy.require('2.0.0')  # Minimum Kivy version

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from datetime import datetime
import json
import os
import io

# App Configuration
Window.size = (800, 600)  # Default window size for desktop; auto-adjusts on mobile

# Data Files
INVENTORY_FILE = 'inventory.json'
HISTORY_FILE = 'history.csv'
CONFIG_FILE = 'config.json'

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        # Logo (use a local image or download one; here assuming a local 'logo.png')
        # For production, include a tooth icon PNG in the app bundle.
        img = Image(source='https://cdn-icons-png.flaticon.com/512/3774/3774278.png', size_hint=(1, 0.3))
        layout.add_widget(img)
        
        title = Label(text='DentalProfit Pro', font_size=32, bold=True)
        subtitle = Label(text='Gestión de costos y precios odontológicos', font_size=18, color=(0.4, 0.4, 0.4, 1))
        
        self.pwd_input = TextInput(hint_text='Clave de licencia', password=True, multiline=False, size_hint=(1, 0.1))
        
        login_btn = Button(text='Iniciar sesión', size_hint=(1, 0.1), background_color=(0.05, 0.4, 0.96, 1))
        login_btn.bind(on_press=self.login)
        
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(self.pwd_input)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        if self.pwd_input.text.strip() == 'dental2026':
            self.manager.current = 'menu'
        else:
            popup = Popup(title='Error', content=Label(text='Clave incorrecta'), size_hint=(0.6, 0.3))
            popup.open()

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='🦷 DentalProfit Pro', font_size=24, bold=True)
        layout.add_widget(title)
        
        btn_dashboard = Button(text='Dashboard', on_press=lambda x: self.change_screen('dashboard'))
        btn_calculator = Button(text='Calculadora de precio', on_press=lambda x: self.change_screen('calculator'))
        btn_inventory = Button(text='Inventario', on_press=lambda x: self.change_screen('inventory'))
        btn_history = Button(text='Historial', on_press=lambda x: self.change_screen('history'))
        btn_config = Button(text='Configuración', on_press=lambda x: self.change_screen('config'))
        btn_logout = Button(text='🚪 Cerrar sesión', on_press=self.logout)
        
        layout.add_widget(btn_dashboard)
        layout.add_widget(btn_calculator)
        layout.add_widget(btn_inventory)
        layout.add_widget(btn_history)
        layout.add_widget(btn_config)
        layout.add_widget(btn_logout)
        
        self.add_widget(layout)
    
    def change_screen(self, screen_name):
        self.manager.current = screen_name
    
    def logout(self, instance):
        # Clear data if needed; for now, just return to login
        self.manager.current = 'login'

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.update_dashboard()
        self.add_widget(self.layout)
    
    def update_dashboard(self):
        self.layout.clear_widgets()
        
        title = Label(text='🏦 Panel de Control', font_size=22, bold=True)
        self.layout.add_widget(title)
        
        # Metrics
        metrics_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        
        costo_minuto = app.costo_hora / 60
        metrics_layout.add_widget(Label(text=f'Costo por minuto: ${costo_minuto:.3f}'))
        metrics_layout.add_widget(Label(text=f'Materiales registrados: {len(app.inventario)}'))
        metrics_layout.add_widget(Label(text=f'Costo hora operador: ${app.costo_hora:.2f}'))
        metrics_layout.add_widget(Label(text=f'Registros guardados: {len(app.historial_precios)}'))
        
        self.layout.add_widget(metrics_layout)
        
        # Pie Chart
        chart_label = Label(text='Distribución típica de costos (ejemplo)', font_size=18)
        self.layout.add_widget(chart_label)
        
        fig, ax = plt.subplots()
        df_ej = pd.DataFrame({
            "Concepto": ["Personal", "Materiales", "Otros gastos", "Utilidad"],
            "Porcentaje": [45, 18, 17, 20]
        })
        ax.pie(df_ej['Porcentaje'], labels=df_ej['Concepto'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        ax.axis('equal')
        
        # Embed Matplotlib in Kivy
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        fig.savefig(output, format='png')
        output.seek(0)
        img = Image(source='', size_hint=(1, 0.5))
        img.texture = kivy.core.image.Image.load_memory(output.getvalue(), ext='png').texture
        self.layout.add_widget(img)
        
        back_btn = Button(text='Volver al menú', size_hint_y=0.1, on_press=self.manager.current = 'menu')
        self.layout.add_widget(back_btn)

class CalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super(CalculatorScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='🧮 Calculadora de precio realista', font_size=22, bold=True)
        layout.add_widget(title)
        
        self.procedimiento = TextInput(hint_text='Nombre del procedimiento', text='Reconstrucción clase II', multiline=False)
        layout.add_widget(self.procedimiento)
        
        self.minutos = TextInput(hint_text='Minutos en sillón', text='45', multiline=False, input_filter='int')
        layout.add_widget(self.minutos)
        
        margen_label = Label(text='Margen de ganancia deseado (%)')
        layout.add_widget(margen_label)
        self.margen = Slider(min=40, max=180, value=100, step=5)
        layout.add_widget(self.margen)
        
        materials_label = Label(text='Materiales utilizados')
        layout.add_widget(materials_label)
        
        self.materials_layout = GridLayout(cols=2, spacing=10)
        self.update_materials()
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        scroll.add_widget(self.materials_layout)
        layout.add_widget(scroll)
        
        calc_btn = Button(text='Calcular', on_press=self.calculate)
        layout.add_widget(calc_btn)
        
        self.result_label = Label(text='', font_size=18)
        layout.add_widget(self.result_label)
        
        save_btn = Button(text='💾 Guardar este cálculo en historial', on_press=self.save)
        layout.add_widget(save_btn)
        
        back_btn = Button(text='Volver al menú', on_press=lambda x: self.manager.current = 'menu')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def update_materials(self):
        self.materials_layout.clear_widgets()
        self.selected_mats = {}
        for mat in app.inventario['Material']:
            chk = Button(text=mat, on_press=self.toggle_material)
            self.materials_layout.add_widget(chk)
            # Quantity input hidden initially
            qty = TextInput(hint_text=f'Cantidad ({app.inventario[app.inventario["Material"] == mat]["Unidad"].iloc[0]})', text='0.1', multiline=False, input_filter='float', disabled=True)
            self.selected_mats[mat] = {'input': qty, 'selected': False}
            self.materials_layout.add_widget(qty)
    
    def toggle_material(self, instance):
        mat = instance.text
        self.selected_mats[mat]['selected'] = not self.selected_mats[mat]['selected']
        self.selected_mats[mat]['input'].disabled = not self.selected_mats[mat]['selected']
    
    def calculate(self, instance):
        try:
            minutos_sillon = int(self.minutos.text)
            margen_deseado = self.margen.value
            
            costo_materiales = 0.0
            for mat, data in self.selected_mats.items():
                if data['selected']:
                    row = app.inventario[app.inventario['Material'] == mat].iloc[0]
                    cant_usada = float(data['input'].text)
                    costo = cant_usada * row['Costo por unidad']
                    costo_materiales += costo
            
            costo_personal = (minutos_sillon / 60) * app.costo_hora
            costo_total = costo_personal + costo_materiales
            precio_final = costo_total * (1 + margen_deseado / 100)
            
            self.result_label.text = (f'Costo de personal: ${costo_personal:.2f}\n'
                                      f'Materiales: ${costo_materiales:.2f}\n'
                                      f'Precio sugerido: ${precio_final:.2f} ({margen_deseado}%)')
            self.precio_final = precio_final
            self.minutos_sillon = minutos_sillon
            self.margen_deseado = margen_deseado
            self.procedimiento_name = self.procedimiento.text
        except ValueError:
            popup = Popup(title='Error', content=Label(text='Ingrese valores válidos'), size_hint=(0.6, 0.3))
            popup.open()
    
    def save(self, instance):
        if hasattr(self, 'precio_final'):
            new_row = {
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Procedimiento': self.procedimiento_name,
                'Precio': round(self.precio_final, 2),
                'Minutos': self.minutos_sillon,
                'Margen': self.margen_deseado
            }
            app.historial_precios = pd.concat([app.historial_precios, pd.DataFrame([new_row])], ignore_index=True)
            app.historial_precios.to_csv(HISTORY_FILE, index=False)
            popup = Popup(title='Éxito', content=Label(text='¡Cálculo guardado!'), size_hint=(0.6, 0.3))
            popup.open()

class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super(InventoryScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='📦 Gestión de inventario', font_size=22, bold=True)
        layout.add_widget(title)
        
        self.grid = GridLayout(cols=5, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        headers = ['Material', 'Precio', 'Cantidad', 'Unidad', 'Costo por unidad']
        for h in headers:
            self.grid.add_widget(Label(text=h, bold=True))
        
        self.inputs = []
        self.update_grid()
        
        scroll = ScrollView()
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        
        add_btn = Button(text='Agregar fila', on_press=self.add_row)
        layout.add_widget(add_btn)
        
        save_btn = Button(text='Guardar cambios', on_press=self.save_inventory)
        layout.add_widget(save_btn)
        
        back_btn = Button(text='Volver al menú', on_press=lambda x: self.manager.current = 'menu')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def update_grid(self):
        for i in range(len(app.inventario)):
            row = app.inventario.iloc[i]
            inputs_row = []
            for col in ['Material', 'Precio', 'Cantidad', 'Unidad']:
                inp = TextInput(text=str(row[col]), multiline=False)
                if col in ['Precio', 'Cantidad']:
                    inp.input_filter = 'float'
                self.grid.add_widget(inp)
                inputs_row.append(inp)
            costo = Label(text=f'${row["Costo por unidad"]:.4f}')
            self.grid.add_widget(costo)
            inputs_row.append(costo)
            self.inputs.append(inputs_row)
    
    def add_row(self, instance):
        inputs_row = []
        for col in ['Material', 'Precio', 'Cantidad', 'Unidad']:
            inp = TextInput(multiline=False)
            if col in ['Precio', 'Cantidad']:
                inp.input_filter = 'float'
            self.grid.add_widget(inp)
            inputs_row.append(inp)
        costo = Label(text='$0.0000')
        self.grid.add_widget(costo)
        inputs_row.append(costo)
        self.inputs.append(inputs_row)
    
    def save_inventory(self, instance):
        data = []
        for row in self.inputs:
            try:
                material = row[0].text
                precio = float(row[1].text) if row[1].text else 0.0
                cantidad = float(row[2].text) if row[2].text else 1.0
                unidad = row[3].text
                costo_unit = precio / cantidad if cantidad != 0 else 0.0
                row[4].text = f'${costo_unit:.4f}'
                data.append({
                    'Material': material,
                    'Precio': precio,
                    'Cantidad': cantidad,
                    'Unidad': unidad,
                    'Costo por unidad': costo_unit
                })
            except ValueError:
                continue  # Skip invalid rows
        app.inventario = pd.DataFrame(data)
        app.inventario.to_json(INVENTORY_FILE, orient='records')
        popup = Popup(title='Éxito', content=Label(text='Inventario guardado'), size_hint=(0.6, 0.3))
        popup.open()

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='📜 Historial de precios calculados', font_size=22, bold=True)
        layout.add_widget(title)
        
        if len(app.historial_precios) == 0:
            layout.add_widget(Label(text='Aún no hay cálculos guardados'))
        else:
            grid = GridLayout(cols=5, spacing=10, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))
            
            headers = ['Fecha', 'Procedimiento', 'Precio', 'Minutos', 'Margen']
            for h in headers:
                grid.add_widget(Label(text=h, bold=True))
            
            for i in range(len(app.historial_precios)):
                row = app.historial_precios.iloc[i]
                grid.add_widget(Label(text=str(row['Fecha'])))
                grid.add_widget(Label(text=str(row['Procedimiento'])))
                grid.add_widget(Label(text=f'${row["Precio"]:.2f}'))
                grid.add_widget(Label(text=str(row['Minutos'])))
                grid.add_widget(Label(text=str(row['Margen'])))
            
            scroll = ScrollView()
            scroll.add_widget(grid)
            layout.add_widget(scroll)
        
        # Download (on desktop/mobile, save to file)
        download_btn = Button(text='Descargar historial (CSV)', on_press=self.download)
        layout.add_widget(download_btn)
        
        back_btn = Button(text='Volver al menú', on_press=lambda x: self.manager.current = 'menu')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def download(self, instance):
        # On mobile/desktop, write to a file in user directory
        with open('historial_precios_dentalprofit.csv', 'w') as f:
            f.write(app.historial_precios.to_csv(index=False))
        popup = Popup(title='Éxito', content=Label(text='Archivo guardado en el directorio actual'), size_hint=(0.6, 0.3))
        popup.open()

class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(text='⚙️ Configuración general', font_size=22, bold=True)
        layout.add_widget(title)
        
        gastos_label = Label(text='Gastos operativos mensuales totales ($)')
        layout.add_widget(gastos_label)
        self.gastos = TextInput(text='4800.0', multiline=False, input_filter='float')
        layout.add_widget(self.gastos)
        
        horas_label = Label(text='Horas efectivas al mes')
        layout.add_widget(horas_label)
        self.horas = TextInput(text='160.0', multiline=False, input_filter='float')
        layout.add_widget(self.horas)
        
        self.result_label = Label(text=f'Costo por hora actual: ${app.costo_hora:.2f}')
        layout.add_widget(self.result_label)
        
        apply_btn = Button(text='Aplicar nuevo costo horario', on_press=self.apply)
        layout.add_widget(apply_btn)
        
        back_btn = Button(text='Volver al menú', on_press=lambda x: self.manager.current = 'menu')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def apply(self, instance):
        try:
            gastos_mensuales = float(self.gastos.text)
            horas_trabajo_mes = float(self.horas.text)
            nuevo_costo_hora = gastos_mensuales / horas_trabajo_mes
            app.costo_hora = nuevo_costo_hora
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'costo_hora': nuevo_costo_hora}, f)
            self.result_label.text = f'Nuevo costo por hora: ${nuevo_costo_hora:.2f}'
            popup = Popup(title='Éxito', content=Label(text='Configuración aplicada'), size_hint=(0.6, 0.3))
            popup.open()
        except ValueError:
            popup = Popup(title='Error', content=Label(text='Ingrese valores válidos'), size_hint=(0.6, 0.3))
            popup.open()

class DentalProfitApp(App):
    def build(self):
        self.load_data()
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(CalculatorScreen(name='calculator'))
        sm.add_widget(InventoryScreen(name='inventory'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(ConfigScreen(name='config'))
        
        return sm
    
    def load_data(self):
        # Inventory
        if os.path.exists(INVENTORY_FILE):
            self.inventario = pd.read_json(INVENTORY_FILE)
        else:
            self.inventario = pd.DataFrame([
                {"Material": "Resina Filtek Supreme", "Precio": 68.50, "Cantidad": 4.0, "Unidad": "g", "Costo por unidad": 68.50/4},
                {"Material": "Adhesivo Scotchbond", "Precio": 135.0, "Cantidad": 5.0, "Unidad": "ml", "Costo por unidad": 135/5},
                {"Material": "Anestesia Articaina 1:100k", "Precio": 48.90, "Cantidad": 50, "Unidad": "carp", "Costo por unidad": 48.90/50},
                {"Material": "Guantes nitrilo", "Precio": 18.50, "Cantidad": 200, "Unidad": "u", "Costo por unidad": 18.50/200},
                {"Material": "Matrix sección", "Precio": 92.0, "Cantidad": 50, "Unidad": "u", "Costo por unidad": 92/50},
            ])
        
        # Config
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.costo_hora = config.get('costo_hora', 28.50)
        else:
            self.costo_hora = 28.50
        
        # History
        if os.path.exists(HISTORY_FILE):
            self.historial_precios = pd.read_csv(HISTORY_FILE)
        else:
            self.historial_precios = pd.DataFrame(columns=["Fecha", "Procedimiento", "Precio", "Minutos", "Margen"])

if __name__ == '__main__':
    app = DentalProfitApp()
    app.run()
quito lambda del botón  

