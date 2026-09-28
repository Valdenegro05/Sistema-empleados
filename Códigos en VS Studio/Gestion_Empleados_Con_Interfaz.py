import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import platform


class Empleado:
    def __init__(self, id_empleado, nombre, email, fecha_inicio_contrato, salario):
        self.__id_empleado = id_empleado
        self.__nombre = nombre
        self.__email = email
        self.__fecha_inicio_contrato = fecha_inicio_contrato
        self.__salario = salario

    @property
    def id_empleado(self): return self.__id_empleado
    @property
    def nombre(self): return self.__nombre
    @property
    def email(self): return self.__email
    @property
    def fecha_inicio_contrato(self): return self.__fecha_inicio_contrato
    @property
    def salario(self): return self.__salario


class Departamento:
    def __init__(self, id_departamento, nombre):
        self.__id_departamento = id_departamento
        self.__nombre = nombre


class Proyecto:
    def __init__(self, id_proyecto, nombre, descripcion, fecha_inicio, estado):
        self.__id_proyecto = id_proyecto
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio
        self.__estado = estado


class BaseDatos:
    def __init__(self, nombre_db="gestion_empleados.db"):
        self.nombre_db = nombre_db
        self.crear_tablas()

    def conectar(self):
        try:
            return sqlite3.connect(self.nombre_db)
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return None

    def crear_tablas(self):
        c = self.conectar()
        if c:
            try:
                cur = c.cursor()
                cur.execute("""CREATE TABLE IF NOT EXISTS empleados (
                    id_empleado TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT NOT NULL,
                    fecha_inicio_contrato TEXT,
                    salario REAL NOT NULL)""")
                c.commit()
            finally:
                c.close()

    def insertar_empleado(self, emp):
        c = self.conectar()
        if c:
            try:
                cur = c.cursor()
                cur.execute("INSERT INTO empleados VALUES (?,?,?,?,?)",
                            (emp.id_empleado, emp.nombre, emp.email,
                             emp.fecha_inicio_contrato, emp.salario))
                c.commit()
                return True, f"{emp.nombre} ha sido registrado."
            except sqlite3.IntegrityError:
                return False, f"El RUT {emp.id_empleado} ya existe."
            except sqlite3.Error as e:
                return False, f"Error: {e}"
            finally:
                c.close()
        return False, "Sin conexion."

    def leer_empleados(self):
        c = self.conectar()
        if c:
            try:
                cur = c.cursor()
                cur.execute("SELECT * FROM empleados ORDER BY nombre")
                return cur.fetchall()
            finally:
                c.close()
        return []

    def actualizar_empleado(self, id_empleado, nuevo_salario):
        c = self.conectar()
        if c:
            try:
                cur = c.cursor()
                cur.execute("UPDATE empleados SET salario=? WHERE id_empleado=?",
                            (nuevo_salario, id_empleado))
                if cur.rowcount > 0:
                    c.commit()
                    return True, f"Remuneracion de {id_empleado} actualizada."
                return False, f"No existe el RUT {id_empleado}."
            finally:
                c.close()
        return False, "Sin conexion."

    def eliminar_empleado(self, id_empleado):
        c = self.conectar()
        if c:
            try:
                cur = c.cursor()
                cur.execute("DELETE FROM empleados WHERE id_empleado=?", (id_empleado,))
                if cur.rowcount > 0:
                    c.commit()
                    return True, f"Empleado {id_empleado} removido."
                return False, f"No existe el RUT {id_empleado}."
            finally:
                c.close()
        return False, "Sin conexion."


class Config:
    def __init__(self, root):
        self.root = root
        self._detectar()

    def _detectar(self):
        self.root.update_idletasks()
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.dpi = self.root.winfo_fpixels("1i")
        self.os = platform.system()
        self.scale = max(1.0, self.dpi / 96.0)
        if self.os == "Darwin":
            self.scale = min(self.scale, 1.10)
        self.win_w = int(min(1200, self.screen_w * 0.82))
        self.win_h = int(min(780, self.screen_h * 0.88))
        self.min_w = int(min(880, self.screen_w * 0.60))
        self.min_h = int(min(560, self.screen_h * 0.55))
        self.sidebar_w = int(self.win_w * 0.22)
        self.f_scale = self.scale if self.scale > 1.0 else 1.0

    def font(self, familia, tam, *estilos):
        return (familia, max(9, int(tam * self.f_scale)), *estilos)


CREMA = "#f4efe6"
CREMA_2 = "#ece5d6"
CREMA_3 = "#e3dac6"
VERDE = "#1e3a2f"
VERDE_2 = "#2a5040"
VERDE_CLARO = "#3d6b57"
DORADO = "#b08d57"
BORDE = "#c9bfa8"
TINTA = "#2b2b2b"
TINTA_SUAVE = "#6b6357"
ROJO = "#7b2d26"
ROJO_2 = "#5e211c"

SERIF = "Georgia"
SERIF_ALT = "Palatino"
SANS = "Helvetica"


class Boton(tk.Label):
    def __init__(self, padre, texto, comando, cfg, bg=VERDE, fg=CREMA,
                 hover=VERDE_2, borde=None, padx=26, pady=12, **kw):
        super().__init__(padre, text=texto, bg=bg, fg=fg,
                         font=cfg.font(SANS, 11, "bold"),
                         padx=padx, pady=pady, cursor="pointinghand", **kw)
        self._bg = bg
        self._hover = hover
        self._comando = comando
        if borde:
            self.configure(highlightthickness=1,
                           highlightbackground=borde,
                           highlightcolor=borde)
        self.bind("<Button-1>", lambda e: self._comando())
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = Config(self)
        self.title("Casa de Personal · Registro de Empleados")
        self.geometry(f"{self.cfg.win_w}x{self.cfg.win_h}")
        self.minsize(self.cfg.min_w, self.cfg.min_h)
        self.configure(bg=CREMA)
        self._centrar()
        self.vista_actual = "registrar"
        self.db = BaseDatos()
        self._estilos()
        self._layout()
        self._vista("registrar")
        self.bind("<Configure>", self._on_resize)

    def _centrar(self):
        self.update_idletasks()
        w, h = self.cfg.win_w, self.cfg.win_h
        x = (self.cfg.screen_w - w) // 2
        y = (self.cfg.screen_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_resize(self, event):
        if not hasattr(self, "tabla"):
            return
        try:
            w = self.tabla.winfo_width()
            if w <= 1:
                return
            self.tabla.column("rut", width=int(w * 0.14))
            self.tabla.column("nombre", width=int(w * 0.22))
            self.tabla.column("email", width=int(w * 0.28))
            self.tabla.column("fecha", width=int(w * 0.16))
            self.tabla.column("salario", width=int(w * 0.20))
        except Exception:
            pass

    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Old.Treeview", background=CREMA_2, foreground=TINTA,
                    fieldbackground=CREMA_2, rowheight=int(34 * self.cfg.f_scale),
                    borderwidth=0, font=self.cfg.font(SERIF, 11))
        s.configure("Old.Treeview.Heading", background=VERDE, foreground=CREMA,
                    font=self.cfg.font(SERIF, 11, "bold"), borderwidth=0, padding=12)
        s.map("Old.Treeview", background=[("selected", DORADO)],
              foreground=[("selected", CREMA)])
        s.map("Old.Treeview.Heading", background=[("active", VERDE_2)])
        s.configure("Old.Vertical.TScrollbar", background=CREMA_2,
                    troughcolor=CREMA, borderwidth=0, arrowsize=12)

    def _layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=VERDE, width=self.cfg.sidebar_w)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        logo = tk.Frame(self.sidebar, bg=VERDE)
        logo.pack(fill="x", pady=(38, 0), padx=28)
        self._monograma(logo)
        tk.Label(logo, text="Casa de Personal", font=self.cfg.font(SERIF, 20, "bold"),
                 bg=VERDE, fg=CREMA).pack(anchor="w", pady=(16, 2))
        tk.Label(logo, text="Est. 1952 · Registro Interno",
                 font=self.cfg.font(SERIF, 11, "italic"),
                 bg=VERDE, fg=DORADO).pack(anchor="w")

        tk.Frame(self.sidebar, bg=DORADO, height=1).pack(fill="x", padx=28, pady=24)
        tk.Label(self.sidebar, text="SECCIONES", font=self.cfg.font(SANS, 9, "bold"),
                 bg=VERDE, fg=DORADO).pack(anchor="w", padx=30, pady=(0, 10))

        self.botones = {}
        items = [("registrar", "Registrar Empleado"),
                 ("listar", "Libro de Personal"),
                 ("actualizar", "Ajustar Remuneracion"),
                 ("eliminar", "Dar de Baja")]
        for key, texto in items:
            fila = tk.Frame(self.sidebar, bg=VERDE)
            fila.pack(fill="x", padx=16, pady=1)
            barra = tk.Frame(fila, bg=VERDE, width=3)
            barra.pack(side="left", fill="y")
            b = tk.Label(fila, text="   " + texto, font=self.cfg.font(SERIF, 13),
                         bg=VERDE, fg=CREMA, anchor="w", padx=18, pady=14,
                         cursor="pointinghand")
            b.pack(side="left", fill="x", expand=True)
            b.bind("<Button-1>", lambda e, k=key: self._vista(k))
            b.bind("<Enter>", lambda e, w=b, br=barra: (
                w.configure(bg=VERDE_2), br.configure(bg=DORADO)))
            b.bind("<Leave>", lambda e, w=b, br=barra, k=key: (
                w.configure(bg=VERDE_2 if self.vista_actual == k else VERDE),
                br.configure(bg=DORADO if self.vista_actual == k else VERDE)))
            self.botones[key] = (b, barra)

        pie = tk.Frame(self.sidebar, bg=VERDE)
        pie.pack(side="bottom", fill="x", pady=20, padx=28)
        tk.Frame(pie, bg=DORADO, height=1).pack(fill="x", pady=(0, 12))
        tk.Label(pie, text="Privado y Confidencial",
                 font=self.cfg.font(SANS, 9, "italic"),
                 bg=VERDE, fg=DORADO).pack(anchor="w")
        tk.Label(pie, text="Edicion I · 2025", font=self.cfg.font(SANS, 8),
                 bg=VERDE, fg=VERDE_CLARO).pack(anchor="w")

        self.main = tk.Frame(self, bg=CREMA)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        head = tk.Frame(self.main, bg=CREMA)
        head.grid(row=0, column=0, sticky="ew", padx=45, pady=(25, 6))
        head.grid_columnconfigure(0, weight=1)
        linea_top = tk.Frame(head, bg=CREMA)
        linea_top.pack(fill="x", pady=(0, 14))
        tk.Frame(linea_top, bg=BORDE, height=1).pack(fill="x", side="top")
        tk.Label(linea_top, text="  *  ", font=self.cfg.font(SANS, 10),
                 bg=CREMA, fg=DORADO).pack(pady=(6, 0))
        self.lbl_titulo = tk.Label(head, text="", font=self.cfg.font(SERIF, 26, "bold"),
                                   bg=CREMA, fg=VERDE)
        self.lbl_titulo.pack(anchor="w")
        self.lbl_sub = tk.Label(head, text="", font=self.cfg.font(SERIF, 13, "italic"),
                                bg=CREMA, fg=TINTA_SUAVE)
        self.lbl_sub.pack(anchor="w", pady=(6, 0))
        orn = tk.Frame(head, bg=CREMA)
        orn.pack(fill="x", pady=(16, 0))
        tk.Frame(orn, bg=DORADO, height=1, width=80).pack(anchor="w")

        self.area = tk.Frame(self.main, bg=CREMA)
        self.area.grid(row=1, column=0, sticky="nsew", padx=45, pady=(15, 25))
        self.area.grid_rowconfigure(0, weight=1)
        self.area.grid_columnconfigure(0, weight=1)

        self.vistas = {}
        self._vista_registrar()
        self._vista_listar()
        self._vista_actualizar()
        self._vista_eliminar()

    def _monograma(self, padre):
        tam = int(64 * self.cfg.f_scale)
        c = tk.Canvas(padre, width=tam, height=tam, bg=VERDE, highlightthickness=0)
        c.pack(anchor="w")
        c.create_oval(2, 2, tam-2, tam-2, outline=DORADO, width=1.5)
        c.create_oval(7, 7, tam-7, tam-7, outline=DORADO, width=0.5)
        c.create_text(tam//2, tam//2 + 1, text="C", fill=DORADO,
                      font=(SERIF_ALT, int(26 * self.cfg.f_scale), "bold"))

    def _scrollable(self, padre):
        contenedor = tk.Frame(padre, bg=CREMA)
        canvas = tk.Canvas(contenedor, bg=CREMA, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical",
                                  command=canvas.yview, style="Old.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        interior = tk.Frame(canvas, bg=CREMA)

        def _on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_config(event):
            canvas.itemconfigure(ventana, width=event.width)

        ventana = canvas.create_window((0, 0), window=interior, anchor="nw")
        interior.bind("<Configure>", _on_config)
        canvas.bind("<Configure>", _on_canvas_config)

        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                if abs(event.delta) < 20:
                    canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
                else:
                    canvas.yview_scroll(int(-event.delta / 120), "units")

        def _bind_wheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_wheel(_):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", _bind_wheel)
        canvas.bind("<Leave>", _unbind_wheel)
        return contenedor, interior

    def _entry(self, padre, placeholder=""):
        wrap = tk.Frame(padre, bg=CREMA_2, highlightthickness=1,
                        highlightbackground=BORDE, highlightcolor=DORADO)
        e = tk.Entry(wrap, font=self.cfg.font(SERIF, 13), bg=CREMA_2, fg=TINTA,
                     insertbackground=TINTA, bd=0, relief="flat", highlightthickness=0)
        e.pack(fill="x", padx=14, pady=10)
        if placeholder:
            e.insert(0, placeholder)
            e.configure(fg=TINTA_SUAVE)
            e.bind("<FocusIn>", lambda ev, en=e, p=placeholder: self._fi(en, p))
            e.bind("<FocusOut>", lambda ev, en=e, p=placeholder: self._fo(en, p))
        return wrap, e

    def _fi(self, entry, ph):
        if entry.get() == ph and entry.cget("fg") == TINTA_SUAVE:
            entry.delete(0, "end")
            entry.configure(fg=TINTA)

    def _fo(self, entry, ph):
        if not entry.get():
            entry.insert(0, ph)
            entry.configure(fg=TINTA_SUAVE)

    def _val(self, entry, ph):
        v = entry.get().strip()
        return "" if (v == ph and entry.cget("fg") == TINTA_SUAVE) else v

    def _label(self, padre, texto):
        return tk.Label(padre, text=texto.upper(), font=self.cfg.font(SANS, 9, "bold"),
                        bg=CREMA_2, fg=TINTA_SUAVE, anchor="w")

    def _card(self, padre):
        outer = tk.Frame(padre, bg=BORDE)
        card = tk.Frame(outer, bg=CREMA_2)
        card.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, card

    def _vista(self, clave):
        self.vista_actual = clave
        for v in self.vistas.values():
            v.pack_forget()
        self.vistas[clave].pack(fill="both", expand=True)
        for k, (lbl, barra) in self.botones.items():
            if k == clave:
                lbl.configure(bg=VERDE_2, fg=CREMA)
                barra.configure(bg=DORADO)
            else:
                lbl.configure(bg=VERDE, fg=CREMA)
                barra.configure(bg=VERDE)
        titulos = {
            "registrar": ("Registrar Empleado", "Incorpore un nuevo miembro al libro de personal."),
            "listar": ("Libro de Personal", "Relacion completa de los empleados en plantilla."),
            "actualizar": ("Ajustar Remuneracion", "Modifique el salario de un empleado por su RUT."),
            "eliminar": ("Dar de Baja", "Remueva a un empleado del registro de forma definitiva."),
        }
        t, s = titulos[clave]
        self.lbl_titulo.configure(text=t)
        self.lbl_sub.configure(text=s)
        if clave == "listar":
            self._refrescar()
    def _vista_registrar(self):
        v = tk.Frame(self.area, bg=CREMA)
        self.vistas["registrar"] = v
        contenedor, interior = self._scrollable(v)
        contenedor.pack(fill="both", expand=True)
        outer, card = self._card(interior)
        outer.pack(fill="x", expand=True, pady=(0, 10))
        inner = tk.Frame(card, bg=CREMA_2)
        inner.pack(fill="both", expand=True, padx=45, pady=28)
        self.entries = {}
        campos = [
            ("rut", "RUT / Identificacion", "Ej: 12.345.678-5"),
            ("nombre", "Nombre completo", "Ej: Juan Perez Gonzalez"),
            ("email", "Correo de contacto", "Ej: juan.perez@empresa.cl"),
            ("fecha", "Fecha de incorporacion", "Formato: YYYY-MM-DD"),
            ("salario", "Remuneracion mensual (CLP)", "Ej: 850000"),
        ]
        for key, etiqueta, ph in campos:
            self._label(inner, etiqueta).pack(anchor="w", pady=(0, 4))
            wrap, e = self._entry(inner, ph)
            wrap.pack(fill="x", pady=(0, 12))
            self.entries[key] = (e, ph)
        botones = tk.Frame(inner, bg=CREMA_2)
        botones.pack(fill="x", pady=(8, 0))
        Boton(botones, "Restablecer", self._limpiar_registro, self.cfg,
              bg=CREMA_3, hover=BORDE, fg=TINTA, borde=BORDE,
              padx=24, pady=10).pack(side="left")
        Boton(botones, "Registrar en el Libro", self._guardar, self.cfg,
              bg=VERDE, hover=VERDE_2, fg=CREMA,
              padx=28, pady=10).pack(side="right")

    def _limpiar_registro(self):
        for e, ph in self.entries.values():
            e.delete(0, "end")
            e.insert(0, ph)
            e.configure(fg=TINTA_SUAVE)

    def _guardar(self):
        rut = self._val(*self.entries["rut"])
        nombre = self._val(*self.entries["nombre"])
        email = self._val(*self.entries["email"])
        fecha = self._val(*self.entries["fecha"])
        sal = self._val(*self.entries["salario"])
        if not all([rut, nombre, email, fecha, sal]):
            messagebox.showwarning("Datos incompletos", "Complete todos los campos.")
            return
        try:
            salario = float(sal.replace(".", "").replace(",", ""))
            if salario <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Remuneracion invalida", "Ingrese un numero positivo.")
            return
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha invalida", "Use formato YYYY-MM-DD.")
            return
        emp = Empleado(rut, nombre, email, fecha, salario)
        ok, msg = self.db.insertar_empleado(emp)
        if ok:
            messagebox.showinfo("Registrado", msg)
            self._limpiar_registro()
        else:
            messagebox.showerror("Error", msg)

    def _vista_listar(self):
        v = tk.Frame(self.area, bg=CREMA)
        self.vistas["listar"] = v
        outer, card = self._card(v)
        outer.pack(fill="both", expand=True)
        top = tk.Frame(card, bg=CREMA_2)
        top.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(top, text="Relacion de empleados", font=self.cfg.font(SERIF, 14, "italic"),
                 bg=CREMA_2, fg=VERDE).pack(side="left")
        Boton(top, "Actualizar Libro", self._refrescar, self.cfg,
              bg=CREMA_3, hover=BORDE, fg=TINTA, borde=BORDE,
              padx=20, pady=8).pack(side="right")
        tk.Frame(card, bg=DORADO, height=1).pack(fill="x", padx=30)
        cont = tk.Frame(card, bg=CREMA_2)
        cont.pack(fill="both", expand=True, padx=30, pady=(14, 24))
        cols = ("rut", "nombre", "email", "fecha", "salario")
        self.tabla = ttk.Treeview(cont, columns=cols, show="headings",
                                  style="Old.Treeview")
        heads = {"rut": "RUT", "nombre": "Nombre", "email": "Correo",
                 "fecha": "Incorporacion", "salario": "Remuneracion"}
        for c in cols:
            self.tabla.heading(c, text=heads[c])
            self.tabla.column(c, anchor="w", width=160)
        self.tabla.column("salario", anchor="e", width=150)
        sb = ttk.Scrollbar(cont, orient="vertical", command=self.tabla.yview,
                           style="Old.Vertical.TScrollbar")
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tabla.tag_configure("odd", background=CREMA_2)
        self.tabla.tag_configure("even", background=CREMA)

    def _refrescar(self):
        for f in self.tabla.get_children():
            self.tabla.delete(f)
        for i, r in enumerate(self.db.leer_empleados()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tabla.insert("", "end", values=(r[0], r[1], r[2], r[3],
                              f"${r[4]:,.0f}"), tags=(tag,))

    def _vista_actualizar(self):
        v = tk.Frame(self.area, bg=CREMA)
        self.vistas["actualizar"] = v
        contenedor, interior = self._scrollable(v)
        contenedor.pack(fill="both", expand=True)
        outer, card = self._card(interior)
        outer.pack(fill="x", expand=True, pady=(0, 10))
        inner = tk.Frame(card, bg=CREMA_2)
        inner.pack(fill="both", expand=True, padx=45, pady=28)
        self._label(inner, "RUT del empleado").pack(anchor="w", pady=(0, 4))
        w1, self.e_act_rut = self._entry(inner, "Ej: 12.345.678-5")
        w1.pack(fill="x", pady=(0, 16))
        self._label(inner, "Nueva remuneracion mensual (CLP)").pack(anchor="w", pady=(0, 4))
        w2, self.e_act_sal = self._entry(inner, "Ej: 950000")
        w2.pack(fill="x", pady=(0, 22))
        Boton(inner, "Confirmar Ajuste", self._actualizar, self.cfg,
              bg=VERDE, hover=VERDE_2, fg=CREMA,
              padx=28, pady=10).pack(anchor="e")

    def _actualizar(self):
        rut = self._val(self.e_act_rut, "Ej: 12.345.678-5")
        sal = self._val(self.e_act_sal, "Ej: 950000")
        if not rut or not sal:
            messagebox.showwarning("Datos incompletos", "Complete ambos campos.")
            return
        try:
            salario = float(sal.replace(".", "").replace(",", ""))
            if salario <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Remuneracion invalida", "Ingrese un numero positivo.")
            return
        ok, msg = self.db.actualizar_empleado(rut, salario)
        if ok:
            messagebox.showinfo("Actualizado", msg)
            self.e_act_rut.delete(0, "end")
            self.e_act_sal.delete(0, "end")
        else:
            messagebox.showerror("Error", msg)

    def _vista_eliminar(self):
        v = tk.Frame(self.area, bg=CREMA)
        self.vistas["eliminar"] = v
        contenedor, interior = self._scrollable(v)
        contenedor.pack(fill="both", expand=True)
        outer, card = self._card(interior)
        outer.pack(fill="x", expand=True, pady=(0, 10))
        inner = tk.Frame(card, bg=CREMA_2)
        inner.pack(fill="both", expand=True, padx=45, pady=28)
        marco = tk.Frame(inner, bg=CREMA_2, highlightthickness=1,
                         highlightbackground=ROJO)
        marco.pack(fill="x", pady=(0, 22))
        contenido = tk.Frame(marco, bg=CREMA_2)
        contenido.pack(fill="x", padx=20, pady=16)
        tk.Label(contenido, text="!", font=self.cfg.font(SERIF, 30),
                 bg=CREMA_2, fg=ROJO).pack(side="left", padx=(0, 16))
        texto = tk.Frame(contenido, bg=CREMA_2)
        texto.pack(side="left", fill="x", expand=True)
        tk.Label(texto, text="Aviso importante", font=self.cfg.font(SERIF, 13, "bold"),
                 bg=CREMA_2, fg=ROJO, anchor="w").pack(anchor="w")
        tk.Label(texto, text="Esta accion es irreversible. El empleado sera removido permanentemente.",
                 font=self.cfg.font(SANS, 10), bg=CREMA_2, fg=TINTA_SUAVE,
                 wraplength=620, justify="left").pack(anchor="w", pady=(2, 0))
        self._label(inner, "RUT del empleado a dar de baja").pack(anchor="w", pady=(0, 4))
        w, self.e_del_rut = self._entry(inner, "Ej: 12.345.678-5")
        w.pack(fill="x", pady=(0, 30))
        Boton(inner, "Dar de Baja Definitivamente", self._eliminar, self.cfg,
              bg=ROJO, hover=ROJO_2, fg=CREMA,
              padx=30, pady=12).pack(anchor="e")

    def _eliminar(self):
        rut = self._val(self.e_del_rut, "Ej: 12.345.678-5")
        if not rut:
            messagebox.showwarning("Campo vacio", "Ingrese el RUT.")
            return
        if not messagebox.askyesno("Confirmar",
                                   f"Desea dar de baja al empleado con RUT {rut}?"):
            return
        ok, msg = self.db.eliminar_empleado(rut)
        if ok:
            messagebox.showinfo("Baja realizada", msg)
            self.e_del_rut.delete(0, "end")
        else:
            messagebox.showerror("Error", msg)


if __name__ == "__main__":
    App().mainloop()                    