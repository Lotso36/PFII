from datetime import datetime

def validar_dni(dni: str) -> bool:
    return dni.isdigit() and len(dni) == 8

def validar_texto_no_vacio(texto: str, min_len: int = 2) -> bool:
    return len(texto.strip()) >= min_len

def validar_fecha(fecha_str: str) -> bool:
    try:
        datetime.strptime(fecha_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def validar_booleano(valor: str) -> bool:
    return valor in ('0', '1')

def validar_entero_positivo(valor: str) -> bool:
    try:
        num = int(valor)
        return num > 0
    except ValueError:
        return False

def solicitar_dato(mensaje: str, funcion_validacion, mensaje_error: str) -> str:
    while True:
        try:
            dato = input(mensaje).strip()
            if not dato:
                print("  [!] El campo no puede estar vacío.")
                continue
            if funcion_validacion(dato):
                return dato
            print(f"  [!] Error de validación: {mensaje_error}")
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada por el usuario.")
            raise