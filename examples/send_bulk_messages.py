import sys
import os
import csv
import time
import logging
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sender import WhatsAppMessageSender
from src.utils import setup_logging

setup_logging()

def validate_phone(phone):
    """Validate phone number format."""
    if not phone:
        return False
    # Eliminar espacios y verificar formato básico
    phone = phone.strip()
    # Debe comenzar con + y tener al menos 10 dígitos
    return phone.startswith('+') and len(phone) >= 10 and phone[1:].replace(' ', '').isdigit()

def validate_name(name):
    """Validate name is not empty and has reasonable length."""
    if not name:
        return False
    name = name.strip()
    return 2 <= len(name) <= 50

def validate_status(status):
    """Validate status field."""
    return status in ['Not Send', 'Sent', 'Error']

def read_guests_from_csv(csv_path):
    """Read guest information from CSV file."""
    guests = []
    skipped = []
    
    print(f"\nLeyendo archivo CSV: {csv_path}")
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as file:  # Agregamos -sig para manejar BOM
            reader = csv.DictReader(file)
            total_rows = sum(1 for row in csv.DictReader(open(csv_path, 'r', encoding='utf-8-sig')))
            print(f"Total de registros en CSV: {total_rows}")
            
            # Reiniciar el archivo para leerlo de nuevo
            file.seek(0)
            reader = csv.DictReader(file)
            
            print(f"Columnas encontradas: {reader.fieldnames}")
            
            for i, row in enumerate(reader, 1):
                name = row.get('Nombre', '').strip()
                phone = row.get('Telefono', '').strip()
                status = row.get('Estado', '').strip()
                
                print(f"\nProcesando registro {i}/{total_rows}:")
                print(f"  Nombre: {name}")
                print(f"  Teléfono: {phone}")
                print(f"  Estado: {status}")
                
                # Solo procesar si el estado es "Not Send"
                if status != 'Not Send':
                    print(f"  → Saltando: estado actual es '{status}'")
                    skipped.append({'nombre': name, 'telefono': phone, 'estado': status, 'razon': 'estado no es Not Send'})
                    continue
                
                if not name or not phone:
                    print("  → Saltando: nombre o teléfono vacío")
                    skipped.append({'nombre': name, 'telefono': phone, 'estado': status, 'razon': 'datos incompletos'})
                    continue
                
                guests.append({'nombre': name, 'telefono': phone, 'estado': status})
                print("  → Agregado a la lista de envío")
                
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {str(e)}")
        return []
    
    # Mostrar resumen
    print("\n=== Resumen de lectura ===")
    print(f"Total de registros en CSV: {total_rows}")
    print(f"Registros válidos para envío: {len(guests)}")
    print(f"Registros saltados: {len(skipped)}")
    
    if skipped:
        print("\nRegistros saltados:")
        for skip in skipped:
            print(f"  • {skip['nombre']} ({skip['telefono']}) - Razón: {skip['razon']}")
    
    return guests

def update_status_in_csv(csv_path, guest_name, new_status='Sent'):
    """Update the status of a guest in the CSV file."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            if row['Nombre'].strip() == guest_name:
                row['Estado'] = new_status
            rows.append(row)
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def create_message(guest_name):
    """Create personalized message using template."""
    return f"""¡Hola *{guest_name}*! 🌟  

Te escribo en nombre de *Alcides y Nilda*, quienes están llenos de emoción y alegría por la celebración de su boda el *25 de enero*. 💍✨  

Para ayudarlos con la organización, por favor confirma cuántas personas de tu grupo o familia asistirán al evento ingresando al siguiente enlace:  

🔗 https://www.alcidesynilda.com/#confirmar

Si lo prefieres, también puedes confirmar por este medio enviándome los siguientes datos:  
- Tu nombre completo.  
- Los nombres de tus acompañantes mayores de 18 años.  

Este día será uno de los momentos más importantes en la vida de Alcides y Nilda, y nos encantaría compartirlo contigo. Tu confirmación es muy importante para que podamos preparar todo con mucho amor y atención a los detalles. 💕  

¡Gracias por ser parte de este momento tan especial para ellos! Estamos seguros de que será un día lleno de alegría y felicidad compartida. 🎉  

Atentamente,  
*Coordinación - Boda Alcides & Nilda*"""

def get_start_time():
    """Calculate start time 15 seconds from now."""
    current = datetime.now()
    start_time = current + timedelta(seconds=15)
    return start_time

def send_bulk_messages(csv_path, delay_seconds=15):
    print(f"\nIntentando leer archivo CSV: {csv_path}")
    guests = read_guests_from_csv(csv_path)
    
    print(f"Total de registros encontrados: {len(guests)}")
    
    if not guests:
        print("❌ No hay registros válidos para procesar")
        return
    
    # Mostrar los primeros registros para verificar
    print("\nPrimeros registros encontrados:")
    for i, guest in enumerate(guests[:3], 1):
        print(f"  {i}. {guest['nombre']} - {guest['telefono']}")
    
    print("\n=== Sistema de Envío de Mensajes WhatsApp ===")
    print("Asegúrate de que WhatsApp Web esté abierto y conectado")
    print(f"Se procesarán {len(guests)} mensajes")
    print("Los mensajes comenzarán a enviarse en 10 segundos...")
    print("Por favor, no cierres el navegador durante el proceso\n")
    
    # Confirmar si queremos continuar
    response = input("¿Deseas continuar con el envío? (s/n): ")
    if response.lower() != 's':
        print("Operación cancelada por el usuario")
        return
    
    time.sleep(10)  # Reducido de 15 a 10 segundos
    
    for i, guest in enumerate(guests, 1):
        try:
            print(f"\nProcesando mensaje {i}/{len(guests)}")
            print(f"Enviando a: {guest['nombre']} ({guest['telefono']})")
            
            sender = WhatsAppMessageSender(
                mode='contact',
                phone_number=guest['telefono'],
                message=create_message(guest['nombre']),
                waiting_time_to_send=10,
                close_tab=True,
                waiting_time_to_close=1
            )
            
            sender.execute()
            
            # Reducir tiempo de espera post-envío
            time.sleep(5)
            
            update_status_in_csv(csv_path, guest['nombre'])
            print(f"✅ Mensaje enviado a {guest['nombre']}")
            
            if i < len(guests):
                print(f"⏳ Esperando {delay_seconds} segundos antes del siguiente mensaje...")
                time.sleep(delay_seconds)
            
        except Exception as e:
            print(f"❌ Error al enviar mensaje a {guest['nombre']}: {str(e)}")
            continue
    
    print("\n=== Proceso de envío completado ===")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python send_bulk_messages.py ruta_al_archivo.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"❌ El archivo {csv_path} no existe")
        sys.exit(1)
    
    print("\n=== Sistema de Envío de Mensajes WhatsApp ===")
    print("Asegúrate de que WhatsApp Web esté abierto y conectado")
    print("Los mensajes comenzarán a enviarse en 10 segundos...")
    print("Por favor, no cierres el navegador durante el proceso\n")
        
    send_bulk_messages(csv_path, delay_seconds=15) 