import pywhatkit
import logging
import pyautogui
import time
from src.utils import setup_logging

setup_logging()

class WhatsAppMessageSender:
    def __init__(self, mode=None, phone_number=None, group_id=None, message=None, time_hour=None, time_minute=None,
                 waiting_time_to_send=15, close_tab=True, waiting_time_to_close=2):
        self.mode = mode
        self.phone_number = phone_number
        self.group_id = group_id
        self.message = message
        self.time_hour = time_hour
        self.time_minute = time_minute
        self.waiting_time_to_send = waiting_time_to_send
        self.close_tab = close_tab
        self.waiting_time_to_close = waiting_time_to_close

    def click_send_button(self):
        """Click the send button using multiple methods."""
        try:
            # 1. Intentar con coordenadas absolutas del botón de enviar
            screen_width, screen_height = pyautogui.size()
            send_button_x = int(screen_width * 0.95)
            send_button_y = int(screen_height * 0.95)
            
            # Primer intento: clic en coordenadas
            pyautogui.moveTo(send_button_x, send_button_y, duration=0.5)
            pyautogui.click()
            time.sleep(1)
            
            # 2. Intentar con múltiples ENTER
            for _ in range(3):
                pyautogui.press('enter')
                time.sleep(0.5)
            
            # 3. Intentar con Ctrl+Enter
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(0.5)
            
            # 4. Intentar buscar y hacer clic en el botón por imagen
            try:
                send_button = pyautogui.locateOnScreen('send_button.png', confidence=0.7)
                if send_button:
                    pyautogui.click(send_button)
            except:
                pass
            
            # 5. Intentar con coordenadas alternativas
            alternative_x = int(screen_width * 0.98)
            alternative_y = int(screen_height * 0.90)
            pyautogui.moveTo(alternative_x, alternative_y, duration=0.5)
            pyautogui.click()
            
            # 6. Un último ENTER para asegurar
            time.sleep(1)
            pyautogui.press('enter')
            
        except Exception as e:
            logging.error(f"Error clicking send button: {e}")
            # Último intento con ENTER si todo lo demás falla
            pyautogui.press('enter')

    def send_message_to_contact(self):
        """Send a WhatsApp message to a contact."""
        try:
            logging.info(f"Sending message to contact: {self.phone_number}")
            pywhatkit.sendwhatmsg_instantly(
                self.phone_number,
                self.message,
                wait_time=10,
                tab_close=False,
                close_time=1
            )
            # Reducir tiempo de espera inicial
            time.sleep(2)
            
            # Un solo intento de envío es suficiente
            self.click_send_button()
            time.sleep(1)
            
            # Cerrar la pestaña
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
                
            logging.info("Message sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send message to contact: {e}")
            raise e

    def send_message_to_group(self):
        """Send a WhatsApp message to a group."""
        try:
            logging.info(f"Sending message to group: {self.group_id}")
            pywhatkit.sendwhatmsg_to_group_instantly(
                self.group_id,
                self.message,
                wait_time=self.waiting_time_to_send,
                tab_close=False,
                close_time=self.waiting_time_to_close
            )
            # Esperar a que la interfaz esté lista
            time.sleep(3)
            
            # Intentar enviar el mensaje de múltiples formas
            self.click_send_button()
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Esperar a que el mensaje se envíe
            time.sleep(5)
            
            # Cerrar la pestaña usando Ctrl+W
            pyautogui.hotkey('ctrl', 'w')
            
            # Esperar un momento después de cerrar
            time.sleep(2)
                
            logging.info("Message sent successfully!")
        except Exception as e:
            logging.error(f"Failed to send message to group: {e}")
            raise e

    def execute(self):
        """Execute the message sending based on the selected mode."""
        if self.mode == "contact":
            self.send_message_to_contact()
        elif self.mode == "group":
            self.send_message_to_group()
