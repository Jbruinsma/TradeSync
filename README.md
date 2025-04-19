# TradeSync

**TradeSync** is a web-based trade copying system that automates and synchronizes trades between a master OANDA account and multiple child accounts. Designed for traders using the OANDA REST v20 API, TradeSync provides a flexible and efficient way to mirror trades across multiple accounts — both live and demo — without requiring the user to stay logged in.

## Key Features

## **Master-to-Multiple Child Copying**  
  One master OANDA account can be linked to multiple child accounts. All trades from the master are mirrored in the child accounts automatically.

- **Web-Based Execution**  
  Entirely web-powered using Flask — no desktop app or constant login required.

- **AVL Tree-Powered Database**  
  TradeSync uses an **AVL Tree** for fast, balanced access to user and account data.

- **Custom Child Settings**  
  Each child account can have its own configuration:
  - Trade size multiplier
  - Accepted trade types (market, limit, stop)
  - Risk management preferences

- **Supports OANDA REST v20 API**  
  Compatible with both **Live** and **Demo** OANDA accounts (more broker support coming soon).

- **Real-Time Execution**  
  Monitors and executes trades in real time using the OANDA REST API.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** AVL Tree (custom data structure for fast lookups and balance)
- **API Integration:** OANDA REST v20
- **Frontend:** HTML, CSS, JavaScript (Flask templating)
- **Version Control:** Git + GitHub
