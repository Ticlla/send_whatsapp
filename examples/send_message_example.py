from src.sender import WhatsAppMessageSender

sender = WhatsAppMessageSender(
    mode='contact',
    phone_number='+59176327232',
    message='Hello, this is a test messagfasdfasde!',
    time_hour=14,
    time_minute=55
)
sender.execute()