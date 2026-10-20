import sqlite3
import pickle
import validaciones as val

DB_NAME = "reniec_db.sqlite"

def obtener_conexion():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"[Error de Conexión]: No se pudo conectar a la base de datos: {e}")
        raise

def inicializar_bd():
    try:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ubigeos (
                id_ubigeo INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_ubigeo TEXT UNIQUE NOT NULL,
                departamento TEXT NOT NULL,
                provincia TEXT NOT NULL,
                distrito TEXT NOT NULL,
                activo BOOLEAN NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ciudadanos (
                id_ciudadano INTEGER PRIMARY KEY AUTOINCREMENT,
                dni TEXT UNIQUE NOT NULL,
                nombres TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                fecha_nacimiento TEXT NOT NULL,
                donante_organos BOOLEAN NOT NULL,
                id_ubigeo INTEGER NOT NULL,
                FOREIGN KEY (id_ubigeo) REFERENCES Ubigeos(id_ubigeo)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sedes (
                id_sede INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_sede TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                capacidad_diaria INTEGER NOT NULL,
                id_ubigeo INTEGER NOT NULL,
                FOREIGN KEY (id_ubigeo) REFERENCES Ubigeos(id_ubigeo)
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tipos_Tramite (
                id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_tramite TEXT NOT NULL,
                costo REAL NOT NULL,
                dias_entrega INTEGER NOT NULL,
                requiere_presencia BOOLEAN NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Solicitudes_Tramite (
                id_solicitud INTEGER PRIMARY KEY AUTOINCREMENT,
                id_ciudadano INTEGER NOT NULL,
                id_sede INTEGER NOT NULL,
                id_tipo INTEGER NOT NULL,
                fecha_solicitud TEXT NOT NULL,
                estado_tramite TEXT NOT NULL,
                FOREIGN KEY (id_ciudadano) REFERENCES Ciudadanos(id_ciudadano),
                FOREIGN KEY (id_sede) REFERENCES Sedes(id_sede),
                FOREIGN KEY (id_tipo) REFERENCES Tipos_Tramite(id_tipo)
            );
            """)

            cursor.execute("SELECT COUNT(*) FROM Ubigeos;")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO Ubigeos (codigo_ubigeo, departamento, provincia, distrito, activo) VALUES ('040101', 'Arequipa', 'Arequipa', 'Arequipa', 1);")
                cursor.execute("INSERT INTO Ubigeos (codigo_ubigeo, departamento, provincia, distrito, activo) VALUES ('040108', 'Arequipa', 'Arequipa', 'José Luis Bustamante y Rivero', 1);")
                cursor.execute("INSERT INTO Tipos_Tramite (nombre_tramite, costo, dias_entrega, requiere_presencia) VALUES ('Emisión DNI Electrónico', 41.0, 10, 1);")
                cursor.execute("INSERT INTO Tipos_Tramite (nombre_tramite, costo, dias_entrega, requiere_presencia) VALUES ('Duplicado DNI Azul', 21.0, 5, 0);")
                cursor.execute("INSERT INTO Sedes (nombre_sede, direccion, telefono, capacidad_diaria, id_ubigeo) VALUES ('OR Arequipa Centro', 'Calle Santo Domingo 118', '054-215010', 450, 1);")
                cursor.execute("INSERT INTO Ciudadanos (dni, nombres, apellidos, fecha_nacimiento, donante_organos, id_ubigeo) VALUES ('74859612', 'Carlos Alberto', 'Mendoza Flores', '14-05-2001', 1, 2);")
                cursor.execute("INSERT INTO Solicitudes_Tramite (id_ciudadano, id_sede, id_tipo, fecha_solicitud, estado_tramite) VALUES (1, 1, 1, '19-10-2026', 'En Proceso');")
                conn.commit()
    except sqlite3.Error as e:
        print(f"[Error Crítico BD]: {e}")
    except Exception as e:
        print(f"[Error Inesperado en Inicialización]: {e}")

def crud_ciudadanos():
    while True:
        print("\n--- GESTIÓN DE TABLA: CIUDADANOS ---")
        print("1. Insertar Ciudadano")
        print("2. Consultar Ciudadanos")
        print("3. Actualizar Ciudadano")
        print("4. Eliminar Ciudadano")
        print("5. Volver al menú principal")
        
        try:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == '1':
                dni = val.solicitar_dato("DNI (8 dígitos): ", val.validar_dni, "El DNI debe tener 8 números.")
                nombres = val.solicitar_dato("Nombres: ", val.validar_texto_no_vacio, "Nombre inválido.")
                apellidos = val.solicitar_dato("Apellidos: ", val.validar_texto_no_vacio, "Apellido inválido.")
                fecha_nac = val.solicitar_dato("Fecha Nacimiento (DD-MM-YYYY): ", val.validar_fecha, "Formato debe ser DD-MM-YYYY.")
                donante = int(val.solicitar_dato("¿Donante de órganos? (1: Sí / 0: No): ", val.validar_booleano, "Ingrese 1 o 0."))
                id_ubigeo = int(val.solicitar_dato("ID de Ubigeo: ", val.validar_entero_positivo, "Debe ser un entero positivo."))

                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Ciudadanos (dni, nombres, apellidos, fecha_nacimiento, donante_organos, id_ubigeo)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (dni, nombres, apellidos, fecha_nac, donante, id_ubigeo))
                    conn.commit()
                    print("[+] Ciudadano registrado con éxito.")

            elif opcion == '2':
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id_ciudadano, dni, nombres, apellidos, fecha_nacimiento, donante_organos, id_ubigeo FROM Ciudadanos;")
                    filas = cursor.fetchall()
                    print("\nID | DNI      | Nombres y Apellidos          | F. Nac     | Donante | ID Ubigeo")
                    print("-" * 78)
                    for f in filas:
                        es_donante = "Sí" if f[5] == 1 else "No"
                        print(f"{f[0]:<2} | {f[1]} | {f[2]} {f[3]:<15} | {f[4]} | {es_donante:<7} | {f[6]}")

            elif opcion == '3':
                id_ciu = int(val.solicitar_dato("ID del ciudadano a actualizar: ", val.validar_entero_positivo, "ID inválido."))
                nuevos_nombres = val.solicitar_dato("Nuevos Nombres: ", val.validar_texto_no_vacio, "Texto vacío.")
                nuevos_apellidos = val.solicitar_dato("Nuevos Apellidos: ", val.validar_texto_no_vacio, "Texto vacío.")
                donante = int(val.solicitar_dato("¿Donante de órganos? (1: Sí / 0: No): ", val.validar_booleano, "Ingrese 1 o 0."))

                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Ciudadanos
                        SET nombres = ?, apellidos = ?, donante_organos = ?
                        WHERE id_ciudadano = ?;
                    """, (nuevos_nombres, nuevos_apellidos, donante, id_ciu))
                    if cursor.rowcount > 0:
                        conn.commit()
                        print("[+] Registro actualizado correctamente.")
                    else:
                        print("[!] No se encontró un ciudadano con ese ID.")

            elif opcion == '4':
                id_ciu = int(val.solicitar_dato("ID del ciudadano a eliminar: ", val.validar_entero_positivo, "ID inválido."))
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Ciudadanos WHERE id_ciudadano = ?;", (id_ciu,))
                    if cursor.rowcount > 0:
                        conn.commit()
                        print("[+] Registro eliminado correctamente.")
                    else:
                        print("[!] No se encontró el ID especificado.")

            elif opcion == '5':
                break
            else:
                print("[!] Opción no válida.")
                
        except sqlite3.IntegrityError as e:
            print(f"[Error de Integridad]: Violación de restricción en base de datos ({e}).")
        except sqlite3.Error as e:
            print(f"[Error de Base de Datos]: {e}")
        except ValueError as e:
            print(f"[Error de Valor]: Entrada numérica o formato no válido ({e}).")
        except Exception as e:
            print(f"[Error Inesperado]: {e}")

def crud_sedes():
    while True:
        print("\n--- GESTIÓN DE TABLA: SEDES RENIEC ---")
        print("1. Insertar Sede")
        print("2. Consultar Sedes")
        print("3. Actualizar Sede")
        print("4. Eliminar Sede")
        print("5. Volver al menú principal")
        
        try:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == '1':
                nombre = val.solicitar_dato("Nombre de la Sede: ", val.validar_texto_no_vacio, "Nombre inválido.")
                direccion = val.solicitar_dato("Dirección: ", val.validar_texto_no_vacio, "Dirección inválida.")
                telefono = val.solicitar_dato("Teléfono: ", val.validar_texto_no_vacio, "Teléfono inválido.")
                capacidad = int(val.solicitar_dato("Capacidad diaria: ", val.validar_entero_positivo, "Entero positivo requerido."))
                id_ubigeo = int(val.solicitar_dato("ID de Ubigeo: ", val.validar_entero_positivo, "Entero positivo requerido."))

                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Sedes (nombre_sede, direccion, telefono, capacidad_diaria, id_ubigeo)
                        VALUES (?, ?, ?, ?, ?);
                    """, (nombre, direccion, telefono, capacidad, id_ubigeo))
                    conn.commit()
                    print("[+] Sede registrada con éxito.")

            elif opcion == '2':
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id_sede, nombre_sede, direccion, telefono, capacidad_diaria, id_ubigeo FROM Sedes;")
                    for f in cursor.fetchall():
                        print(f"ID: {f[0]} | Sede: {f[1]} | Dir: {f[2]} | Tel: {f[3]} | Cap: {f[4]} | Ubigeo: {f[5]}")

            elif opcion == '3':
                id_sede = int(val.solicitar_dato("ID de la sede a actualizar: ", val.validar_entero_positivo, "ID inválido."))
                nueva_dir = val.solicitar_dato("Nueva Dirección: ", val.validar_texto_no_vacio, "Dirección inválida.")
                nueva_cap = int(val.solicitar_dato("Nueva Capacidad Diaria: ", val.validar_entero_positivo, "Número inválido."))

                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Sedes SET direccion = ?, capacidad_diaria = ? WHERE id_sede = ?;
                    """, (nueva_dir, nueva_cap, id_sede))
                    if cursor.rowcount > 0:
                        conn.commit()
                        print("[+] Sede actualizada correctamente.")
                    else:
                        print("[!] No se encontró la sede.")

            elif opcion == '4':
                id_sede = int(val.solicitar_dato("ID de la sede a eliminar: ", val.validar_entero_positivo, "ID inválido."))
                with obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Sedes WHERE id_sede = ?;", (id_sede,))
                    if cursor.rowcount > 0:
                        conn.commit()
                        print("[+] Sede eliminada.")
                    else:
                        print("[!] No se encontró la sede.")

            elif opcion == '5':
                break
            else:
                print("[!] Opción inválida.")
                
        except sqlite3.IntegrityError as e:
            print(f"[Error de Integridad]: {e}")
        except sqlite3.Error as e:
            print(f"[Error de Base de Datos]: {e}")
        except ValueError as e:
            print(f"[Error de Valor]: {e}")
        except Exception as e:
            print(f"[Error Inesperado]: {e}")

def menu_consultas():
    print("\n--- MÓDULO DE CONSULTAS RENIEC ---")
    print("1. Consulta 1: Listado de Ciudadanos con su Ubicación")
    print("2. Consulta 2: Reporte detallado de Solicitudes de Trámite")
    
    try:
        opcion = input("Seleccione la consulta (1 o 2): ").strip()
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            lineas_resultado = []

            if opcion == '1':
                query = """
                SELECT c.dni, c.nombres, c.apellidos, u.distrito, u.provincia, u.departamento
                FROM Ciudadanos c
                INNER JOIN Ubigeos u ON c.id_ubigeo = u.id_ubigeo;
                """
                cursor.execute(query)
                filas = cursor.fetchall()
                lineas_resultado.append("DNI      | Ciudadano                    | Ubicación (Distrito - Prov - Depto)")
                lineas_resultado.append("-" * 75)
                for f in filas:
                    lineas_resultado.append(f"{f[0]} | {f[1]} {f[2]:<15} | {f[3]} - {f[4]} - {f[5]}")

            elif opcion == '2':
                query = """
                SELECT s.id_solicitud, c.dni, c.nombres || ' ' || c.apellidos AS ciudadano,
                       t.nombre_tramite, t.costo, se.nombre_sede, s.fecha_solicitud, s.estado_tramite
                FROM Solicitudes_Tramite s
                INNER JOIN Ciudadanos c ON s.id_ciudadano = c.id_ciudadano
                INNER JOIN Tipos_Tramite t ON s.id_tipo = t.id_tipo
                INNER JOIN Sedes se ON s.id_sede = se.id_sede;
                """
                cursor.execute(query)
                filas = cursor.fetchall()
                lineas_resultado.append("ID | DNI      | Ciudadano            | Trámite                 | Costo | Sede               | Fecha      | Estado")
                lineas_resultado.append("-" * 115)
                for f in filas:
                    lineas_resultado.append(f"{f[0]:<2} | {f[1]} | {f[2]:<20} | {f[3]:<23} | S/{f[4]:<4}| {f[5]:<18} | {f[6]} | {f[7]}")
            else:
                print("[!] Opción de consulta inválida.")
                return

            print("\nRESULTADOS:")
            for linea in lineas_resultado:
                print(linea)

            guardar = input("\n¿Desea guardar los resultados en un archivo .txt? (s/n): ").strip().lower()
            if guardar == 's':
                nombre_archivo = input("Ingrese el nombre del archivo (ej. reporte.txt): ").strip()
                if not nombre_archivo.endswith(".txt"):
                    nombre_archivo += ".txt"
                with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                    for linea in lineas_resultado:
                        archivo.write(linea + "\n")
                print(f"[+] Archivo guardado como '{nombre_archivo}'.")

    except sqlite3.Error as e:
        print(f"[Error de Base de Datos]: {e}")
    except IOError as e:
        print(f"[Error de E/S de Archivo]: {e}")
    except Exception as e:
        print(f"[Error Inesperado]: {e}")

def menu_exportar():
    tablas_validas = {
        '1': 'Ubigeos',
        '2': 'Ciudadanos',
        '3': 'Sedes',
        '4': 'Tipos_Tramite',
        '5': 'Solicitudes_Tramite'
    }
    print("\n--- EXPORTAR TABLA ---")
    for k, v in tablas_validas.items():
        print(f"{k}. {v}")
    
    try:
        op_tabla = input("Seleccione la tabla (1-5): ").strip()
        if op_tabla not in tablas_validas:
            print("[!] Selección inválida.")
            return

        nombre_tabla = tablas_validas[op_tabla]
        formato = input("Seleccione formato (1: Archivo TXT / 2: Archivo Pickle): ").strip()

        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {nombre_tabla};")
            registros = cursor.fetchall()
            nombres_columnas = [descripcion[0] for descripcion in cursor.description]

        if formato == '1':
            archivo_txt = f"export_{nombre_tabla.lower()}.txt"
            with open(archivo_txt, "w", encoding="utf-8") as f:
                f.write(" | ".join(nombres_columnas) + "\n")
                f.write("-" * 60 + "\n")
                for reg in registros:
                    f.write(" | ".join(map(str, reg)) + "\n")
            print(f"[+] Tabla exportada en TXT como '{archivo_txt}'.")

        elif formato == '2':
            archivo_pkl = f"export_{nombre_tabla.lower()}.pkl"
            datos_exportar = {"columnas": nombres_columnas, "datos": registros}
            with open(archivo_pkl, "wb") as f:
                pickle.dump(datos_exportar, f)
            print(f"[+] Tabla serializada en Pickle como '{archivo_pkl}'.")
        else:
            print("[!] Formato no reconocido.")

    except sqlite3.Error as e:
        print(f"[Error de Base de Datos]: {e}")
    except IOError as e:
        print(f"[Error de Archivo]: {e}")
    except pickle.PickleError as e:
        print(f"[Error de Serialización Pickle]: {e}")
    except Exception as e:
        print(f"[Error Inesperado]: {e}")

def menu_principal():
    inicializar_bd()
    while True:
        print("\n==============================================")
        print("   SISTEMA DE GESTIÓN RENIEC - MENÚ PRINCIPAL ")
        print("==============================================")
        print("1. Tabla: Ciudadanos")
        print("2. Tabla: Sedes")
        print("3. Consultas")
        print("4. Exportar")
        print("5. Salir")
        
        try:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == '1':
                crud_ciudadanos()
            elif opcion == '2':
                crud_sedes()
            elif opcion == '3':
                menu_consultas()
            elif opcion == '4':
                menu_exportar()
            elif opcion == '5':
                print("Saliendo del sistema...")
                break
            else:
                print("[!] Opción inválida.")
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo del sistema de forma segura...")
            break
        except Exception as e:
            print(f"[Error Crítico en Menú]: {e}")

if __name__ == "__main__":
    menu_principal()