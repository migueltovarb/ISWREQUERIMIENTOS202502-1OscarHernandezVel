# Author: Oscar Felipe Hernandez
# Connect.me: programa de consola para gestionar contactos
# Date: 2025/10/7
# Version: 1.0

class Contacto:
    def __init__(self, nombre, telefono, email, cargo):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.cargo = cargo
        self.num = None
        
    def guardar_contacto(self):
        try:
            with open("contactos.csv", "r") as archivo:
                num = sum(1 for _ in archivo) + 1
        except FileNotFoundError:
            num = 1

        with open("contactos.csv", "a") as archivo:
            archivo.write(f"{num},{self.nombre},{self.telefono},{self.email},{self.cargo}\n")
            print(f"Contacto #{num} guardado exitosamente.")
    
    def mostrar_contactos(self):
        list = []
        with open("contactos.csv", "r") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) != 5:
                    continue  
                num, nombre, telefono, email, cargo = partes
                contacto = Contacto(nombre, telefono, email, cargo)
                contacto.num = num
                list.append(contacto)
        return list
    
    def buscar_contacto(self, nombre, email):
        contactos = self.mostrar_contactos()
        for contacto in contactos:
            if contacto.nombre == nombre or contacto.email == email:
                return contacto
        return None

    def eliminar_contacto(self, numero):
        contactos = self.mostrar_contactos()
        with open("contactos.csv", "w") as archivo:
            for contacto in contactos:
                if contacto.num != numero:
                    archivo.write(f"{contacto.num},{contacto.nombre},{contacto.telefono},{contacto.email},{contacto.cargo}\n")
        print("Contacto eliminado si existía.")

    def actualizar_contacto(self, numero, nuevo_nombre, nuevo_telefono, nuevo_email, nuevo_cargo):
        contactos = self.mostrar_contactos()
        with open("contactos.csv", "w") as archivo:
            for contacto in contactos:
                if contacto.num == numero:
                    archivo.write(f"{contacto.num},{nuevo_nombre},{nuevo_telefono},{nuevo_email},{nuevo_cargo}\n")
                else:
                    archivo.write(f"{contacto.num},{contacto.nombre},{contacto.telefono},{contacto.email},{contacto.cargo}\n")
        print("Contacto actualizado si existía.")

def __main__():
    while True:
        print("\n--- Menú de Contactos ---")
        print("1. Guardar nuevo contacto")
        print("2. Mostrar todos los contactos")
        print("3. Buscar contacto por nombre o correo")
        print("4. Eliminar contacto por numero de id")
        print("5. Actualizar contacto por numero de id")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre: ")
            telefono = input("Teléfono: ")
            email = input("Email: ")
            cargo = input("Cargo: ")
            contacto = Contacto(nombre, telefono, email, cargo)
            contacto.guardar_contacto()
        elif opcion == "2":
            contacto = Contacto("", "", "", "")
            contactos = contacto.mostrar_contactos()
            print("\nLista de contactos:")
            for c in contactos:
                print(f"Número: {c.num}, Nombre: {c.nombre}, Teléfono: {c.telefono}, Email: {c.email}, Cargo: {c.cargo}")
        elif opcion == "3":
            nombre = input("Ingrese el nombre o correo a buscar: ")
            contacto = Contacto("", "", "", "")
            resultado = contacto.buscar_contacto(nombre)
            if resultado:
                print(f"Encontrado: Nombre: {resultado.nombre}, Teléfono: {resultado.telefono}, Email: {resultado.email}, Cargo: {resultado.cargo}")
            else:
                print("Contacto no encontrado.")
        elif opcion == "4":
            numero = input("Ingrese el numero del contacto a eliminar: ")
            contacto = Contacto("", "", "", "")
            contacto.eliminar_contacto(numero)
        elif opcion == "5":
            numero = input("Ingrese el número del contacto a actualizar: ")
            nuevo_nombre = input("Nuevo nombre: ")
            nuevo_telefono = input("Nuevo teléfono: ")
            nuevo_email = input("Nuevo email: ")
            nuevo_cargo = input("Nuevo cargo: ")
            contacto = Contacto("", "", "", "")
            contacto.actualizar_contacto(numero, nuevo_nombre, nuevo_telefono, nuevo_email, nuevo_cargo)
        elif opcion == "6":
            print("¡Nos vemos pronto!")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    __main__()