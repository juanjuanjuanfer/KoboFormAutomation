from listener.webhook_listener import WebhookListener

if __name__ == "__main__":
    listener = WebhookListener()
    listener.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        listener.stop()