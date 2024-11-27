import flet as ft
import qrcode
import requests
import json
from datetime import datetime
import threading
import os
import time

def main(page: ft.Page):
    page.title = "Barra de navegacion"
    page.bgcolor = ft.colors.WHITE

    # Leer el RUT desde el archivo JSON
    userId = read_user_id()

    qr_image_control = ft.Image()
    update_interval = 60  # Intervalo de actualización en segundos
    qr_update_thread = None
    stop_qr_update = threading.Event()

    # Evento de cambio de navegación
    def on_navigation_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            show_acceso()
        elif selected_index == 1:
            show_noticias()
        elif selected_index == 2:
            show_mis_datos()
        elif selected_index == 3:
            show_notificaciones()
        page.update()

    # Función del selected index 0
    def show_acceso():
        page.controls.clear()
        page.add(ft.Container(
            content=qr_image_control,
            alignment=ft.alignment.center,
            expand=True
        ))
        page.add(navigation_bar)
        start_qr_update_thread()

    # Función para generar el código QR
    def generate_qr_code():
        update_qr_code()

    # Función para actualizar el código QR
    def update_qr_code():
        current_time = datetime.now().strftime("%d%m%y%H%M%S")
        qr_data = f"{userId}{current_time}"

        # Eliminar el archivo del código QR existente si existe
        if os.path.exists("qr_code.png"):
            os.remove("qr_code.png")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr_code.png")
        qr_image_control.src = "qr_code.png"
        send_qr_to_server(qr_data, current_time)
        page.update()

    # Función para enviar el QR al servidor
    def send_qr_to_server(qr_data, current_time):
        url = "http://192.99.70.157:9999/guardar_qr"
        json_body = {
            "RUT": userId,
            "qr_code": qr_data,
            "fecha_hora": current_time
        }
        try:
            response = requests.post(url, json=json_body)
            response.raise_for_status()  # Lanzar una excepción si la solicitud falla
            print("QR guardado exitosamente")
        except requests.RequestException as e:
            print(f"Error al guardar QR: {e}")

    # Función para iniciar el hilo de actualización del QR
    def start_qr_update_thread():
        nonlocal qr_update_thread
        stop_qr_update.clear()
        if qr_update_thread is None or not qr_update_thread.is_alive():
            qr_update_thread = threading.Thread(target=qr_update_loop, daemon=True)
            qr_update_thread.start()

    # Función para detener el hilo de actualización del QR
    def stop_qr_update_thread():
        stop_qr_update.set()
        if qr_update_thread is not None:
            qr_update_thread.join()

    # Función del bucle de actualización del QR
    def qr_update_loop():
        while not stop_qr_update.is_set():
            generate_qr_code()
            time.sleep(update_interval)

    # Función para mostrar noticias
    def show_noticias():
        stop_qr_update_thread()
        page.controls.clear()

        # Crear un WebView para mostrar el contenido de la URL
        web_view = ft.WebView(
            url="http://192.99.70.157:9999/anuncios",
            expand=True,
            on_page_started=lambda _: print("Page started"),
            on_page_ended=lambda _: print("Page ended"),
            on_web_resource_error=lambda e: print("Page error:", e.data),
        )

        page.add(web_view)
        page.add(navigation_bar)
        page.update()

    # Función para mostrar mis datos
    def show_mis_datos():
        stop_qr_update_thread()
        page.controls.clear()

        # Crear un WebView para mostrar el contenido de la URL
        web_view = ft.WebView(
            url=f"http://192.99.70.157:9999/usuario/{userId}",
            expand=True,
            on_page_started=lambda _: print("Page started"),
            on_page_ended=lambda _: print("Page ended"),
            on_web_resource_error=lambda e: print("Page error:", e.data),
        )

        page.add(web_view)
        page.add(navigation_bar)
        page.update()

    # Función para mostrar notificaciones
    def show_notificaciones():
        stop_qr_update_thread()
        page.controls.clear()

        # Crear un WebView para mostrar el contenido de la URL
        web_view = ft.WebView(
            url=f"http://192.99.70.157:9999/recordatorios/{userId}",
            expand=True,
            on_page_started=lambda _: print("Page started"),
            on_page_ended=lambda _: print("Page ended"),
            on_web_resource_error=lambda e: print("Page error:", e.data),
        )

        page.add(web_view)
        page.add(navigation_bar)
        page.update()

    # Crear la barra de navegación
    navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_navigation_change,
        destinations=[
            ft.NavigationBarDestination(icon=ft.icons.QR_CODE, label="Acceso"),
            ft.NavigationBarDestination(icon=ft.icons.NEWSPAPER, label="Noticias"),
            ft.NavigationBarDestination(icon=ft.icons.PERSON_OUTLINE, label="Mis datos"),
            ft.NavigationBarDestination(icon=ft.icons.NOTIFICATIONS, label="Notificaciones"),
        ],
        bgcolor=ft.colors.BLUE_GREY_900,
        indicator_color=ft.colors.AMBER,
    )

    # Estilos CSS personalizados para la barra de navegación
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.WHITE,
            on_primary=ft.colors.BLUE_GREY_900,
            background=ft.colors.BLUE_GREY_900,
            on_background=ft.colors.WHITE,
            surface=ft.colors.BLUE_GREY_900,
            on_surface=ft.colors.WHITE,
            error=ft.colors.RED,
            on_error=ft.colors.WHITE,
        )
    )

    # Agregar la barra de navegación a la página
    page.add(navigation_bar)

    # Iniciar el hilo de actualización del QR
    start_qr_update_thread()

    # Mostrar la vista de "Acceso" por defecto
    show_acceso()

def read_user_id():
    if os.path.exists("config.json"):
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            return config.get("RUT", "123456789")  # Valor predeterminado si no se encuentra el RUT
    else:
        return "123456789"  # Valor predeterminado si el archivo no existe

ft.app(target=main)
