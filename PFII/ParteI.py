from datetime import datetime


class ErrorFormatoRegistro(Exception):
    pass


class ErrorMontoInvalido(Exception):
    pass


def crear_archivo_entrada(nombre_archivo):
    datos = (
        "01/10/2026, Juan, 345.00\n"
        "01/10/2026, Maria,515.00\n"
        "01/10/2026, Saul, 1000,00\n"
        "02/10/2026, Jose, 313.00\n"
        "02/10/2026, Cesar, 420.00\n"
        "02/10/2026, Jorge, 543.00"
    )
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(datos)
    except OSError as e:
        print(f"Error al crear el archivo de entrada: {e}")


def validar_fecha(fecha_texto):
    try:
        datetime.strptime(fecha_texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def procesar_ventas(archivo_entrada, archivo_salida):
    ventas_por_dia = {}
    total_ventas = 0.0

    try:
        with open(archivo_entrada, "r", encoding="utf-8") as archivo_csv:
            lineas = archivo_csv.readlines()

            if not lineas:
                raise ValueError("El archivo CSV esta vacio.")

            for num_linea, linea in enumerate(lineas, start=1):
                linea = linea.strip()
                if not linea:
                    continue

                try:
                    partes = linea.split(",", 2)
                    if len(partes) < 3:
                        raise ErrorFormatoRegistro(
                            f"Linea {num_linea}: Faltan columnas en el registro."
                        )

                    fecha = partes[0].strip()
                    vendedor = partes[1].strip()
                    monto_str = partes[2].strip().replace(",", ".")

                    if not validar_fecha(fecha):
                        raise ErrorFormatoRegistro(
                            f"Linea {num_linea}: Fecha '{fecha}' no cumple el formato DD/MM/AAAA."
                        )

                    if not vendedor:
                        raise ErrorFormatoRegistro(
                            f"Linea {num_linea}: El nombre del vendedor esta vacio."
                        )

                    try:
                        monto = float(monto_str)
                    except ValueError:
                        raise ErrorMontoInvalido(
                            f"Linea {num_linea}: El valor '{partes[2].strip()}' no es un numero valido."
                        )

                    if monto < 0:
                        raise ErrorMontoInvalido(
                            f"Linea {num_linea}: El monto no puede ser negativo ({monto})."
                        )

                    ventas_por_dia[fecha] = ventas_por_dia.get(fecha, 0.0) + monto
                    total_ventas += monto

                except (ErrorFormatoRegistro, ErrorMontoInvalido) as error_validacion:
                    print(f"Advertencia de validacion -> {error_validacion}")

        if not ventas_por_dia:
            raise ValueError("No se encontraron registros validos para procesar.")

        print("Ventas por dia:")
        for fecha, suma_dia in ventas_por_dia.items():
            print(f"{fecha}: {suma_dia:.2f}")

        print(f"\nTotal de ventas: {total_ventas:.2f}")

        with open(archivo_salida, "wb") as archivo_bin:
            contenido_binario = f"{total_ventas:.2f}\n".encode("utf-8")
            archivo_bin.write(contenido_binario)

    except FileNotFoundError:
        print(f"Error: No se encontro el archivo '{archivo_entrada}'.")
    except PermissionError:
        print("Error: Permisos insuficientes para leer o escribir los archivos.")
    except ValueError as e:
        print(f"Error de datos: {e}")
    except OSError as e:
        print(f"Error del sistema de archivos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


def leer_archivo_binario(archivo_salida):
    try:
        with open(archivo_salida, "rb") as archivo_bin:
            datos = archivo_bin.read().decode("utf-8").strip()
            print(f"\nContenido leido de {archivo_salida}:")
            print(datos)
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo_salida}' no existe.")
    except UnicodeDecodeError:
        print(f"Error: No se pudo decodificar el archivo '{archivo_salida}'.")
    except OSError as e:
        print(f"Error al leer el archivo binario: {e}")


if __name__ == "__main__":
    archivo_csv = "Entrada.csv"
    archivo_bin = "Salida.bin"

    crear_archivo_entrada(archivo_csv)
    procesar_ventas(archivo_csv, archivo_bin)
    leer_archivo_binario(archivo_bin)