import pandas as pd
import os
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))

def menu():
    print("---BIENVENIDO AL CAJERO AUTOMÁTICO---")
    print("Por favor selecciona lo que quieras hacer:\n")
    print("1) Crear nueva cuenta")
    print("2) Retirar dinero")
    print("3) Ingresar dinero")
    print("4) Consulta estado de cuenta")
    print("5) Mostrar gráficos")
    print("6) Salir\n")

def leerClientes():
    try:
        path = os.path.join(script_dir, 'clientes.xlsx')
        print(f"Leyendo clientes desde: {path}")
        df = pd.read_excel(path, engine='openpyxl')
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce') 
        df['DNI'] = df['DNI'].astype(str)  
        return df
    except FileNotFoundError:
        print("Archivo clientes.xlsx no encontrado, creando nuevo DataFrame.")
        return pd.DataFrame(columns=['DNI', 'Nombre', 'Apellido', 'Edad', 'Monto'])

def guardarClientes(clientes_df):
    path = os.path.join(script_dir, 'clientes.xlsx')
    print(f"Guardando clientes en: {path}")
    clientes_df.to_excel(path, index=False, engine='openpyxl')
    print("Clientes guardados.")

def leerTransacciones():
    try:
        path = os.path.join(script_dir, 'transacciones.xlsx')
        print(f"Leyendo transacciones desde: {path}")
        df = pd.read_excel(path, engine='openpyxl')
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce') 
        df['DNI'] = df['DNI'].astype(str)  
        return df
    except FileNotFoundError:
        print("Archivo transacciones.xlsx no encontrado, creando nuevo DataFrame.")
        return pd.DataFrame(columns=['DNI', 'Tipo', 'Monto'])

def guardarTransacciones(transacciones_df):
    path = os.path.join(script_dir, 'transacciones.xlsx')
    print(f"Guardando transacciones en: {path}")
    transacciones_df.to_excel(path, index=False, engine='openpyxl')
    print("Transacciones guardadas.")

clientes_df = leerClientes()
transacciones_df = leerTransacciones()

def crearNuevaCuenta():
    global clientes_df
    dni = input("Ingrese su DNI, por favor (8 dígitos):\n")
    dni = dni.strip()  
    if len(dni) == 8 and dni.isdigit():
        if not clientes_df.empty and dni in clientes_df['DNI'].values:
            print("Error: Este DNI ya tiene una cuenta registrada.\n")
            return

        nombre = input("Ingrese su nombre, por favor:\n")
        apellido = input("Ingrese su apellido, por favor:\n")
        edad = int(input("Ingrese su edad, por favor:\n"))
        if edad < 18:
            print("Error: Solo mayores de edad pueden aperturar una cuenta en este banco.\n")
            return 
        
        monto_opcion = input("¿Desea realizar un depósito a su cuenta? (Sí o No):\n").lower()
        monto = int(input("Ingrese el monto a depositar:\nS/")) if monto_opcion == "si" else 0
        
        nueva_cuenta = pd.DataFrame([{'DNI': dni, 'Nombre': nombre, 'Apellido': apellido, 'Edad': edad, 'Monto': monto}])
        print("Nueva cuenta creada:", nueva_cuenta)
        clientes_df = pd.concat([clientes_df, nueva_cuenta], ignore_index=True)
        print("Clientes DataFrame actualizado:", clientes_df)
        guardarClientes(clientes_df)
        
        print(f"Cuenta creada con éxito para {nombre} {apellido}.\n")
    else:
        print("Error: DNI inválido.\n")

def encontrarCuentaPorDni(dni):
    global clientes_df
    cuenta = clientes_df[clientes_df['DNI'] == dni]
    return cuenta.iloc[0] if not cuenta.empty else None

def retirarDinero():
    global clientes_df, transacciones_df
    dni = input("Ingrese su DNI para proceder al retiro:\n")
    dni = dni.strip()  
    cuenta = encontrarCuentaPorDni(dni)
    
    if cuenta is not None:
        cantidad = int(input("¿Cuánto dinero desea retirar?\nS/"))
        if cantidad <= cuenta['Monto']:
            saldo_anterior = cuenta['Monto']
            clientes_df.loc[clientes_df['DNI'] == dni, 'Monto'] -= cantidad
            transacciones_df = pd.concat([transacciones_df, pd.DataFrame([{'DNI': dni, 'Tipo': 'Retiro', 'Monto': cantidad}])], ignore_index=True)
            guardarClientes(clientes_df)
            guardarTransacciones(transacciones_df)
            print(f"Saldo anterior: S/{saldo_anterior}\nSaldo actual: S/{saldo_anterior - cantidad}\n")
        else:
            print("Fondos insuficientes.\n")
    else:
        print("No se encontró una cuenta con ese DNI.\n")

def ingresarDinero():
    global clientes_df, transacciones_df
    dni = input("Ingrese su DNI para proceder al depósito:\n")
    dni = dni.strip()  
    cuenta = encontrarCuentaPorDni(dni)
    
    if cuenta is not None:
        cantidad = int(input("¿Cuánto dinero desea ingresar?\nS/"))
        saldo_anterior = cuenta['Monto']
        clientes_df.loc[clientes_df['DNI'] == dni, 'Monto'] += cantidad
        transacciones_df = pd.concat([transacciones_df, pd.DataFrame([{'DNI': dni, 'Tipo': 'Depósito', 'Monto': cantidad}])], ignore_index=True)
        guardarClientes(clientes_df)
        guardarTransacciones(transacciones_df)
        print(f"Saldo anterior: S/{saldo_anterior}\nSaldo actual: S/{saldo_anterior + cantidad}\n")
    else:
        print("No se encontró una cuenta con ese DNI.\n")

def consultarEstadoCuenta():
    global transacciones_df
    dni = input("Ingrese su DNI para consultar el estado de su cuenta:\n")
    dni = dni.strip()  
    cuenta = encontrarCuentaPorDni(dni)
    
    if cuenta is not None:
        print(f"Saldo actual: S/{cuenta['Monto']}\n")
        
        
        transacciones_cuenta = transacciones_df[transacciones_df['DNI'] == dni]
        if not transacciones_cuenta.empty:
            transacciones_cuenta_grouped = transacciones_cuenta.groupby('Tipo')['Monto'].sum()
            plt.figure(figsize=(10, 6))
            plt.pie(transacciones_cuenta_grouped, labels=transacciones_cuenta_grouped.index, autopct='%1.1f%%', startangle=140)
            plt.title(f'Transacciones para la cuenta {dni}')
            plt.show()
        else:
            print("No se encontraron transacciones para esta cuenta.\n")
    else:
        print("No se encontró una cuenta con ese DNI.\n")

def mostrarGraficos():
    global clientes_df, transacciones_df   
    
    transacciones_tipo = transacciones_df['Tipo'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(transacciones_tipo, labels=transacciones_tipo.index, autopct='%1.1f%%', startangle=140)
    plt.title('Distribución de Tipos de Transacciones')
    plt.show()
    
    top_cuentas = clientes_df.nlargest(5, 'Monto')
    plt.figure(figsize=(10, 6))
    plt.bar(top_cuentas['Nombre'] + ' ' + top_cuentas['Apellido'], top_cuentas['Monto'])
    plt.xlabel('Clientes')
    plt.ylabel('Monto (S/)')
    plt.title('Top 5 Cuentas con Más Fondos')
    plt.show()
    
    depositos = transacciones_df[transacciones_df['Tipo'] == 'Depósito']
    top_depositos = depositos.groupby('DNI')['Monto'].sum().nlargest(5)
    top_depositos = top_depositos.reset_index()
    top_depositos = top_depositos.merge(clientes_df[['DNI', 'Nombre', 'Apellido']], on='DNI')
    plt.figure(figsize=(10, 6))
    plt.bar(top_depositos['Nombre'] + ' ' + top_depositos['Apellido'], top_depositos['Monto'])
    plt.xlabel('Clientes')
    plt.ylabel('Monto Total de Depósitos (S/)')
    plt.title('Top 5 Personas con Mayores Depósitos')
    plt.show()
    
    retiros = transacciones_df[transacciones_df['Tipo'] == 'Retiro']
    top_retiros = retiros.groupby('DNI')['Monto'].sum().nlargest(5)
    top_retiros = top_retiros.reset_index()
    top_retiros = top_retiros.merge(clientes_df[['DNI', 'Nombre', 'Apellido']], on='DNI')
    plt.figure(figsize=(10, 6))
    plt.bar(top_retiros['Nombre'] + ' ' + top_retiros['Apellido'], top_retiros['Monto'])
    plt.xlabel('Clientes')
    plt.ylabel('Monto Total de Retiros (S/)')
    plt.title('Top 5 Personas con Mayores Retiros')
    plt.show()

def confirmarSalida():
    return input("¿Estás seguro de que deseas salir? (Sí o No):\n").lower() == "si"

def main():
    while True:
        menu()
        try:
            opcion = int(input("Elija una opción (1-6):\n"))
            if opcion == 1:
                crearNuevaCuenta()
            elif opcion == 2:
                retirarDinero()
            elif opcion == 3:
                ingresarDinero()
            elif opcion == 4:
                consultarEstadoCuenta()
            elif opcion == 5:
                mostrarGraficos()
            elif opcion == 6:
                if confirmarSalida():
                    break
            else:
                print("Opción no válida.\n")
        except ValueError:
            print("Ingrese un número válido.\n")

main()