import os
import ast
import operator
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard

# --- MOTOR MATEMÁTICO SEGURO ---
class EvaluadorSeguro:
    def _init_(self):
        self.operadores = {
            ast.Add: operator.add, 
            ast.Sub: operator.sub, 
            ast.Mult: operator.mul, 
            ast.Div: operator.truediv,
            ast.USub: operator.neg
        }

    def evaluar(self, expresion: str) -> float:
        try:
            tree = ast.parse(expresion, mode='eval')
            return self._evaluar_nodo(tree.body)
        except Exception:
            raise ValueError("Expresión inválida")

    def _evaluar_nodo(self, nodo):
        if isinstance(nodo, ast.Constant):
            return nodo.value
        elif isinstance(nodo, ast.BinOp):
            left = self._evaluar_nodo(nodo.left)
            right = self._evaluar_nodo(nodo.right)
            return self.operadores[type(nodo.op)](left, right)
        elif isinstance(nodo, ast.UnaryOp):
            operand = self._evaluar_nodo(nodo.operand)
            return self.operadores[type(nodo.op)](operand)
        else:
            raise TypeError(f"Operación no soportada: {type(nodo)}")

# --- GESTIÓN DE ALMACENAMIENTO ---
class GestorAlmacenamiento:
    @staticmethod
    def obtener_ruta() -> str:
        try:
            return os.path.join(App.get_running_app().user_data_dir, "tasa_config.txt")
        except AttributeError:
            return "tasa_config.txt"

    @classmethod
    def cargar_tasa(cls) -> float:
        ruta = cls.obtener_ruta()
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return float(f.read().strip())
            except (ValueError, IOError):
                return 0.0
        return 0.0

    @classmethod
    def guardar_tasa(cls, tasa: float) -> bool:
        try:
            with open(cls.obtener_ruta(), "w", encoding="utf-8") as f:
                f.write(str(tasa))
            return True
        except IOError:
            return False

# --- VENTANA EMERGENTE ---
class PopupTasa(Popup):
    entrada_tasa = ObjectProperty(None)

    def _init_(self, app_principal, **kwargs):
        super()._init_(**kwargs)
        self.app_principal = app_principal
        self.title = "Establecer Tasa"
        self.size_hint = (0.85, 0.35)
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        layout.add_widget(Label(text="Introduce la tasa oficial (Bs/$):", font_size='16sp'))
        
        tasa_actual = GestorAlmacenamiento.cargar_tasa()
        self.entrada_tasa = TextInput(
            text=str(tasa_actual) if tasa_actual > 0 else "",
            multiline=False, input_filter='float', input_type='number',
            halign='center', font_size='22sp'
        )
        layout.add_widget(self.entrada_tasa)
        
        btn_guardar = Button(text="Guardar", font_size='16sp', bold=True)
        btn_guardar.bind(on_release=self.aplicar_tasa)
        layout.add_widget(btn_guardar)
        self.content = layout

    def aplicar_tasa(self, instance):
        try:
            nueva_tasa = float(self.entrada_tasa.text)
            if nueva_tasa > 0 and GestorAlmacenamiento.guardar_tasa(nueva_tasa):
                self.app_principal.tasa_texto = f"Tasa del día: {nueva_tasa:,.2f} Bs/$"
                self.dismiss()
                self.app_principal.interfaz_raiz.calcular_operacion()
        except ValueError:
            pass

# --- DISEÑO ---
Builder.load_string('''
<CalculadoraInterfaz>:
    orientation: 'vertical'
    padding: [20, 15, 20, 15]
    spacing: 14
    BoxLayout:
        size_hint_y: None
        height: '45dp'
        Label:
            text: app.tasa_texto
            font_size: '15sp'
        Button:
            text: "⚙️ Configurar"
            size_hint_x: None
            width: '110dp'
            on_release: root.abrir_menu_tasa()
    BoxLayout:
        size_hint_y: None
        height: '45dp'
        Label:
            text: "Modo: " + ("USD" if not app.modo_inverso else "VES")
        Button:
            text: "⇅ Alternar"
            size_hint_x: None
            width: '110dp'
            on_release: root.alternar_modo()
    TextInput:
        id: entrada_operacion
        hint_text: "Introduce montos"
        multiline: False
        halign: 'center'
        font_size: '28sp'
        size_hint_y: None
        height: '65dp'
        input_filter: lambda text, from_undo: text if text in '0123456789+-*/.xX ' else ''
        on_text: root.calcular_operacion()
    Label:
        text: "TOTAL USD: " + app.resultado_usd
    Label:
        text: "TOTAL VES: " + app.resultado_bs
''')

class CalculadoraInterfaz(BoxLayout):
    def _init_(self, app_principal, **kwargs):
        super()._init_(**kwargs)
        self.app_principal = app_principal
        self.evaluador = EvaluadorSeguro()

    def abrir_menu_tasa(self):
        PopupTasa(self.app_principal).open()

    def alternar_modo(self):
        self.app_principal.modo_inverso = not self.app_principal.modo_inverso
        self.calcular_operacion()

    def calcular_operacion(self):
        tasa = GestorAlmacenamiento.cargar_tasa()
        expresion = self.ids.entrada_operacion.text.lower().replace('x', '*')
        if not expresion.strip():
            self.app_principal.resultado_usd = "$ 0.00"
            self.app_principal.resultado_bs = "Bs. 0.00"
            return
        try:
            monto = float(self.evaluador.evaluar(expresion))
            if not self.app_principal.modo_inverso:
                usd = monto
                ves = usd * tasa
            else:
                ves = monto
                usd = ves / tasa if tasa > 0 else 0.0
            self.app_principal.resultado_usd = f"$ {usd:,.2f}"
            self.app_principal.resultado_bs = f"Bs. {ves:,.2f}"
        except:
            self.app_principal.resultado_usd = "..."
            self.app_principal.resultado_bs = "..."

class CalculadoraDivisasApp(App):
    tasa_texto = StringProperty("Cargando...")
    resultado_usd = StringProperty("$ 0.00")
    resultado_bs = StringProperty("Bs. 0.00")
    modo_inverso = BooleanProperty(False)

    def build(self):
        self.interfaz_raiz = CalculadoraInterfaz(self)
        return self.interfaz_raiz

    def on_start(self):
        tasa = GestorAlmacenamiento.cargar_tasa()
        if tasa > 0:
            self.tasa_texto = f"Tasa: {tasa:,.2f} Bs/$"
        else:
            self.interfaz_raiz.abrir_menu_tasa()

if _name_ == '_main_':
    CalculadoraDivisasApp().run()
