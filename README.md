# 💸 Budget Tracker (CSV) v2

Aplicación de consola en **Python** para registrar y gestionar gastos usando un archivo **CSV**.  
Incluye funcionalidades de agregar, listar, editar, eliminar y generar reportes con filtros.

# 💸 Budget Tracker (CSV) v2

A console application in **Python** to record and manage expenses using a **CSV** file.  
Includes features to add, list, edit, delete, and generate reports with filters.

---

## 🚀 Basic Usage


```bash
# Agregar gastos
python main.py add 2025-08-24 comida 12.50 "Tacos"
python main.py add 2025-08-25 transporte 3.00 "Bus"
python main.py add 2025-09-01 renta 450 "Septiembre"

# Listar gastos
python main.py list
python main.py list --month 2025-08
python main.py list --category comida

# Editar/eliminar gastos
python main.py edit 1 --amount 15.00 --note "Cena"
python main.py delete 2

# Reportes
python main.py report month 2025-08
python main.py report month 2025-08 --export agosto.csv
python main.py report category
python main.py report overview
python main.py report range 2025-08-01 2025-08-31
