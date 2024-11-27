import flet as ft
from flet import TextField, ElevatedButton, Row, Column, Text, Image
from flet_core.control_event import ControlEvent
import requests
import json
import os
import subprocess
import sys

def main(page: ft.Page) -> None:
    page.title = "Login"
    page.bgcolor = ft.colors.WHITE

    # Ruta de la imagen local
    image_path = "assets/images/logo.png"

    # Control de imagen
    logo_image = Image(src=image_path, width=200, height=200)  # Agrandar el logo

    username_text: TextField = TextField(
        label="Rut", text_align=ft.TextAlign.LEFT, width=200
    )
    clave_text: TextField = TextField(
        label="Clave", text_align=ft.TextAlign.LEFT, width=200, password=True
    )
    submit_button: ElevatedButton = ElevatedButton(
        text="Ingresar", disabled=True, width=200
    )

    def validate(param: ControlEvent) -> None:
        if all([username_text.value, clave_text.value]):
            submit_button.disabled = False
        else:
            submit_button.disabled = True
        page.update()

    def submit(param: ControlEvent) -> None:
        rut = username_text.value
        clave = clave_text.value

        # URL de la API
        api_url = "http://192.99.70.157:9999/login"

        # Datos a enviar a la API
        data = {
            "RUT": rut,
            "Clave": clave
        }

        try:
            # Realizar la solicitud POST a la API
            response = requests.post(api_url, json=data)
            response.raise_for_status()  # Lanzar una excepción si la solicitud falla

            # Imprimir la respuesta completa para diagnosticar
            print(response.text)

            response_json = response.json()
            if response_json.get("error") is None:
                # Guardar el RUT en un archivo JSON
                with open("config.json", "w") as config_file:
                    json.dump({"RUT": rut}, config_file)

                # Ejecutar el código de navegacion.py en un proceso separado
                subprocess.Popen([sys.executable, "navegacion.py"])

                # Cerrar la ventana de la aplicación de Flet
                page.window.destroy()
            else:
                page.clean()
                page.add(
                    Row(
                        controls=[
                            Text(
                                value="Invalid credentials", size=20, disabled=False
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
        except requests.RequestException as e:
            page.clean()
            page.add(
                Row(
                    controls=[
                        Text(
                            value=f"Error connecting to the API: {e}", size=20, disabled=False
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )

    username_text.on_change = validate
    clave_text.on_change = validate
    submit_button.on_click = submit

    page.add(
        Row(
            controls=[
                Column(
                    [
                        logo_image,  # Agregar la imagen encima del formulario
                        username_text,
                        clave_text,
                        submit_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

if __name__ == '__main__':
    ft.app(target=main)
