import sqlite3
from datetime import date

# ==========================================
# 1. CLASES BASADAS EN EL DIAGRAMA UML
# ==========================================

class Empleado:
    """Clase Empleado sin contraseña ni campos extra."""
    def __init__(self, id_empleado: str, nombre: str, email: str,
                 fecha_inicio_contrato: str, salario: float):
        self.__id_empleado = id_empleado  # RUT (Texto)
        self.__nombre = nombre
        self.__email = email
        self.__fecha_inicio_contrato = fecha_inicio_contrato
        self.__salario = salario

    # Getters
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

    # Métodos del UML
    def registrar_empleado(self):
        pass

    def actualizar_datos(self):
        pass


class Departamento:
    def __init__(self, id_departamento: int, nombre: str):
        self.__id_departamento = id_departamento
        self.__nombre = nombre

    @property
    def id_departamento(self): return self.__id_departamento
    @property
    def nombre(self): return self.__nombre


class Proyecto:
    def __init__(self, id_proyecto: int, nombre: str, descripcion: str, fecha_inicio: str, estado: str):
        self.__id_proyecto = id_proyecto
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio
        self.__estado = estado

    @property
    def id_proyecto(self): return self.__id_proyecto
    @property
    def nombre(self): return self.__nombre
    @property
    def descripcion(self): return self.__descripcion
    @property
    def fecha_inicio(self): return self.__fecha_inicio
    @property
    def estado(self): return self.__estado


# ==========================================
# 2. GESTOR DE BASE DE DATOS Y CRUD
# ==========================================

class BaseDatos:
    """Maneja la conexión y las operaciones CRUD usando SQLite."""
    def __init__(self, nombre_db="gestion_empleados.db"):
        self.nombre_db = nombre_db
        self.crear_tablas()

    def conectar(self):
        try:
            return sqlite3.connect(self.nombre_db)
        except sqlite3.Error as e:
            print(f"[-] Error de conexión: {e}")
            return None

    def crear_tablas(self):
        """Crea la tabla de empleados sin contraseña."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS empleados (
                        id_empleado TEXT PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        email TEXT NOT NULL,
                        fecha_inicio_contrato TEXT,
                        salario REAL NOT NULL
                    )
                """)
                conexion.commit()
            except sqlite3.Error as e:
                print(f"[-] Error al crear la tabla: {e}")
            finally:
                conexion.close()

    def insertar_empleado(self, emp: Empleado):
        """Inserta un empleado."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO empleados (id_empleado, nombre, email, fecha_inicio_contrato, salario)
                    VALUES (?, ?, ?, ?, ?)
                """, (emp.id_empleado, emp.nombre, emp.email,
                      emp.fecha_inicio_contrato, emp.salario))
                conexion.commit()
                print(f"[+] Empleado '{emp.nombre}' registrado con éxito.")
            except sqlite3.IntegrityError:
                print(f"[-] Error: El RUT {emp.id_empleado} ya se encuentra registrado.")
            except sqlite3.Error as e:
                print(f"[-] Error al insertar: {e}")
            finally:
                conexion.close()

    def leer_empleados(self):
        """Obtiene todos los empleados."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM empleados")
                return cursor.fetchall()
            except sqlite3.Error as e:
                print(f"[-] Error al leer datos: {e}")
                return []
            finally:
                conexion.close()

    def actualizar_empleado(self, id_empleado: str, nuevo_salario: float):
        """Actualiza el salario del empleado buscando por su RUT."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE empleados SET salario = ? WHERE id_empleado = ?
                """, (nuevo_salario, id_empleado))
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"[+] Salario del empleado RUT {id_empleado} actualizado.")
                else:
                    print(f"[-] No se encontró un empleado con el RUT {id_empleado}.")
            except sqlite3.Error as e:
                print(f"[-] Error al actualizar: {e}")
            finally:
                conexion.close()

    def eliminar_empleado(self, id_empleado: str):
        """Elimina un empleado por su RUT."""
        conexion = self.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM empleados WHERE id_empleado = ?", (id_empleado,))
                if cursor.rowcount > 0:
                    conexion.commit()
                    print(f"[+] Empleado con RUT {id_empleado} eliminado.")
                else:
                    print(f"[-] No se encontró un empleado con el RUT {id_empleado}.")
            except sqlite3.Error as e:
                print(f"[-] Error al eliminar: {e}")
            finally:
                conexion.close()


# ==========================================
# 3. MENÚ DE CONSOLA
# ==========================================

def menu():
    db = BaseDatos()

    while True:
        print("\n--- GESTIÓN DE EMPLEADOS ---")
        print("1. Registrar Empleado")
        print("2. Listar Empleados")
        print("3. Actualizar Salario de Empleado")
        print("4. Eliminar Empleado")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            rut = input("Ingrese ID / RUT del empleado (ej. 12345678-9): ")
            nombre = input("Nombre completo: ")
            email = input("Email: ")
            fecha_contrato = input("Fecha de inicio contrato (YYYY-MM-DD): ")

            try:
                salario = float(input("Salario: "))
                emp = Empleado(rut, nombre, email, fecha_contrato, salario)
                db.insertar_empleado(emp)
            except ValueError:
                print("[-] Error: El salario debe ser un valor numérico válido (ej. 750000.0).")

        elif opcion == "2":
            print("\n--- LISTADO DE EMPLEADOS ---")
            registros = db.leer_empleados()
            if not registros:
                print("No hay registros.")
            else:
                for r in registros:
                    print(f"RUT: {r[0]} | Nombre: {r[1]} | Email: {r[2]} | Contrato: {r[3]} | Salario: ${r[4]:,.0f}")

        elif opcion == "3":
            rut = input("Ingrese el RUT del empleado a actualizar: ")
            try:
                nuevo_salario = float(input("Ingrese el nuevo salario: "))
                db.actualizar_empleado(rut, nuevo_salario)
            except ValueError:
                print("[-] Error: El salario debe ser un número válido.")

        elif opcion == "4":
            rut = input("Ingrese el RUT del empleado a eliminar: ")
            db.eliminar_empleado(rut)

        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu()