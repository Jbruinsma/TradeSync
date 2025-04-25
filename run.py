from app import create_app
from config import Config
import asyncio
from app.services.copier import TradeCopier
import threading
from app import user_db

app = create_app(Config)

def run_trade_copier(trade_copier):
    async def copier_main():
        user_db.add_observer(trade_copier)
        trade_copier.start()
        print("Trade copier started.")
        await trade_copier.run()
    
    asyncio.run(copier_main())

if __name__ == '__main__':
    copier = TradeCopier()
    copier_thread = threading.Thread(target=run_trade_copier, args=(copier,))
    copier_thread.start()

    try:
        app.run(debug=True, use_reloader=False)
    finally:
        copier.stop()
        copier_thread.join()
