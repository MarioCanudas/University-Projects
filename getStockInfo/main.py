# getStockInfo - Aplicación para obtener información de acciones en la bolsa
# 
# INSTALACIÓN DE DEPENDENCIAS:
# Antes de ejecutar la aplicación, instala las librerías necesarias con pip:
# 
#     pip install typer
#     pip install rich
#     pip install yfinance
#     pip install pandas
# 
# O instala todas las dependencias de una vez:
# 
#     pip install typer rich yfinance pandas
# 
# REQUISITOS:
# - Python 3.12 o superior
import typer
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box
import yfinance as yf
import pandas as pd

# Objeto Typer: Crea la aplicación de línea de comandos (CLI)
# Permite definir comandos y opciones que el usuario puede ejecutar desde la terminal
# Ejemplo: python main.py info AAPL --period 1mo
# Se usa a lo largo de la app para:
# - Definir comandos con @app.command() (info, ayuda, menu)
# - Configurar el punto de entrada principal con @app.callback()
# - Ejecutar la aplicación al final con app()
# - Gestionar argumentos y opciones de los comandos (symbol, period, etc.)
app = typer.Typer()

# Objeto Console: Proporciona funcionalidades de impresión mejoradas con Rich
# Permite mostrar texto con colores, estilos, tablas y paneles en la terminal
# Mejora la experiencia visual de la aplicación comparado con print() estándar
# Se usa a lo largo de la app para:
# - Mostrar mensajes con colores (rojo para errores, verde para éxito, amarillo para advertencias)
# - Imprimir tablas formateadas con la información de las acciones (mostrar_info_basica, mostrar_resumen)
# - Mostrar paneles decorativos (bienvenida, ayuda)
# - Indicadores de estado durante la carga de datos (console.status)
# - Menús interactivos con formato mejorado
# - Mensajes informativos y de error al usuario
console = Console()

# Períodos válidos aceptados por yfinance
VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

def validar_periodo(period):
    # Valida si el período proporcionado es un período válido de yfinance
    if not period or not isinstance(period, str):
        return False
    return period.lower() in [p.lower() for p in VALID_PERIODS]

def get_stock_metrics(symbol, period):
    # Valida el período antes de usarlo
    if not validar_periodo(period):
        console.print(f"[red]Error: Período '{period}' no es válido.[/red]")
        console.print(f"[yellow]Períodos válidos: {', '.join(VALID_PERIODS)}[/yellow]")
        return {}
    
    # Obtiene el ticker y el historial de precios
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    
    # Verifica que haya datos suficientes
    if hist.empty or len(hist) < 2:
        return {}
    
    # Calcula precios actual y anterior
    precio_actual = hist["Close"].iloc[-1]
    precio_anterior = hist["Close"].iloc[-2]
    
    # Calcula el cambio y el cambio porcentual
    cambio = precio_actual - precio_anterior
    cambio_porcentual = cambio / precio_anterior if precio_anterior > 0 else 0.0
    
    # Calcula volatilidad y ratio de Sharpe
    std_close = hist["Close"].std()
    mean_close = hist["Close"].mean()
    ratio_sharpe = mean_close / std_close if std_close > 0 else 0.0
    
    # Construye el diccionario con todas las métricas
    metrics = {
        "precio": float(precio_actual),
        "cambio": float(cambio),
        "cambioPorcentual": float(cambio_porcentual),
        "volumen": float(hist["Volume"].iloc[-1]),
        "volumenPromedio": float(hist["Volume"].mean()),
        "volumenTotal": float(hist["Volume"].sum()),
        "volatilidad": float(std_close),
        "ratioSharpe": float(ratio_sharpe),
        "maximaGanancia": float(hist["Close"].max()),
        "maximaPerdida": float(hist["Close"].min()),
    }
    
    # Filtra valores NaN
    result = {k: v for k, v in metrics.items() if not pd.isna(v)}
    
    return result

def get_stock_info(symbol, period):
    # Obtiene información básica de la acción y sus métricas
    ticker = yf.Ticker(symbol)
    
    info = {
        "símbolo": symbol,
        "nombre": ticker.info.get("longName", ticker.info.get("shortName", "N/A")),
        "sector": ticker.info.get("sector", "N/A"),
        "industria": ticker.info.get("industry", "N/A"),
        "país": ticker.info.get("country", "N/A"),
        "métricas": get_stock_metrics(symbol, period),
    }
    
    return info

def bienvenida():
    # Muestra el mensaje de bienvenida de la aplicación
    titulo = Text(
        "getStockInfo",
        style="bold",
        justify="center",
    )
    
    subtitle = Text(
        "Desarrollado con yfinance, typer y rich", 
        style="bold", 
        justify="center"
    )
    
    panel = Panel(
        Text(
            "Utiliza esta herramienta para obtener un resumen rápido de cualquier acción en la bolsa.", 
            style="bold", 
            justify="center"
        ),
        title=titulo, 
        subtitle=subtitle,
        border_style="blue", 
        width=80
    )

    console.print(panel)


def mostrar_ayuda():
    # Muestra información de ayuda sobre cómo encontrar símbolos de acciones
    ayuda_panel = Panel(
        Text(
            "Para encontrar el símbolo de una acción, puedes buscar en:\n\n"
            "• Yahoo Finance: https://finance.yahoo.com/\n"
            "  - Busca el nombre de la empresa y encontrarás su símbolo\n"
            "  - Ejemplo: 'Apple' → AAPL\n\n"
            "• Google Finance: https://www.google.com/finance/\n"
            "  - Similar a Yahoo Finance, con búsqueda de empresas\n\n"
            "• MarketWatch: https://www.marketwatch.com/\n"
            "  - Incluye búsqueda de símbolos y listados completos\n\n"
            "Ejemplos de símbolos comunes:\n"
            "• AAPL - Apple Inc.\n"
            "• MSFT - Microsoft Corporation\n"
            "• GOOGL - Alphabet Inc. (Google)\n"
            "• TSLA - Tesla, Inc.\n"
            "• AMZN - Amazon.com, Inc.\n"
            "• META - Meta Platforms Inc. (Facebook)\n\n"
            "Nota: Los símbolos deben estar en mayúsculas y corresponder\n"
            "a acciones listadas en bolsas de valores como NYSE, NASDAQ, etc.",
            style="white",
            justify="left"
        ),
        title="[bold cyan]Ayuda: Cómo encontrar símbolos de acciones[/bold cyan]",
        border_style="yellow",
        width=90
    )
    
    console.print()
    console.print(ayuda_panel)
    console.print()
    console.print("[bold]Presiona Enter para continuar...[/bold]")
    input()


def validar_stock_data(stock_data):
    # Valida que los datos de la acción sean válidos
    if stock_data is None:
        return False
    
    # Verifica que tenga nombre válido y métricas
    nombre = stock_data.get('nombre', 'N/A')
    metricas = stock_data.get('métricas', {})
    
    tiene_nombre_valido = nombre != "N/A" and nombre.strip() != ""
    tiene_metricas = len(metricas) > 0
    
    return tiene_nombre_valido and tiene_metricas


def obtener_stock_valido(symbol, period):
    # Obtiene y valida datos de una acción, pidiendo otro símbolo si el actual no es válido
    while True:
        console.print()
        with console.status(f"[bold green]Obteniendo información de {symbol.upper()}..."):
            stock_data = get_stock_info(symbol, period)
        
        if validar_stock_data(stock_data):
            return stock_data
        else:
            console.print(f"[red]No se pudo obtener información válida para {symbol.upper()}[/red]")
            console.print("[yellow]El símbolo puede ser incorrecto o la acción no tiene datos disponibles.[/yellow]")
            console.print("[cyan]💡 Tip: Usa el comando 'ayuda' o la opción 2 del menú para ver cómo encontrar símbolos válidos.[/cyan]")
            
            # Pregunta si desea intentar con otro símbolo
            continuar = typer.prompt(
                "\n¿Deseas intentar con otro símbolo? (s/n)",
                default="s"
            )
            
            if continuar.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                symbol = typer.prompt("Ingresa un nuevo símbolo de la acción (e.g., AAPL, MSFT, TSLA)")
            else:
                return None


def mostrar_info_basica(stock_data):
    # Muestra solo la información básica de la acción (sin métricas)
    symbol = stock_data.get('símbolo', 'N/A').upper()
    nombre = stock_data.get('nombre', 'N/A')
    sector = stock_data.get('sector', 'N/A')
    industria = stock_data.get('industria', 'N/A')
    pais = stock_data.get('país', 'N/A')
    
    # Crea y muestra la tabla con la información básica
    tabla_info = Table(title=f"Información de {symbol}", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    tabla_info.add_column("Campo", style="cyan", no_wrap=True)
    tabla_info.add_column("Valor", style="green")
    tabla_info.add_row("Nombre", nombre)
    tabla_info.add_row("Símbolo", symbol)
    tabla_info.add_row("Sector", sector)
    tabla_info.add_row("Industria", industria)
    tabla_info.add_row("País", pais)
    
    console.print(tabla_info)


def seleccionar_metricas():
    # Menú interactivo para seleccionar qué métricas mostrar
    categorias = {
        "1": "Precios",
        "2": "Volumen",
        "3": "Riesgo",
        "4": "Todas"
    }
    
    console.print("\n[bold cyan]Selecciona las métricas a mostrar:[/bold cyan]")
    console.print("1. Precios (Precio actual, cambio, máximos/mínimos)")
    console.print("2. Volumen (Volumen actual, promedio, total)")
    console.print("3. Riesgo (Volatilidad, Sharpe ratio, retornos)")
    console.print("4. Todas las métricas")
    
    seleccion = typer.prompt("\nSelecciona una opción (1-4)", default="4")
    
    if seleccion == "4":
        return ["precios", "volumen", "riesgo"]
    elif seleccion in categorias:
        return [categorias[seleccion].lower()]
    else:
        console.print("[yellow]Opción no válida, mostrando todas las métricas[/yellow]")
        return ["precios", "volumen", "riesgo"]


def menu_stock_actual(stock_data, period):
    # Menú para interactuar con la acción actual
    symbol = stock_data.get('símbolo', 'N/A').upper()
    
    while True:
        console.print(f"\n[bold cyan]Menú para {symbol}[/bold cyan]")
        console.print("1. Ver métricas de la acción")
        console.print("2. Cambiar de acción")
        console.print("3. Volver al menú principal")
        
        opcion = typer.prompt("\nSelecciona una opción", default="1")
        
        if opcion == "1":
            # Muestra el menú de selección de métricas y luego las métricas
            metricas_seleccionadas = seleccionar_metricas()
            console.print()
            mostrar_resumen(stock_data, metricas_seleccionadas)
        
        elif opcion == "2":
            # Permite cambiar de acción
            nuevo_symbol = typer.prompt("Ingresa el nuevo símbolo de la acción (e.g., AAPL, MSFT, TSLA)")
            
            # Valida el período con bucle de reintento
            while True:
                nuevo_period = typer.prompt(
                    "Período de datos históricos", 
                    default=period,
                    show_default=True
                )
                if validar_periodo(nuevo_period):
                    break
                else:
                    console.print(f"[red]Error: Período '{nuevo_period}' no es válido.[/red]")
                    console.print(f"[yellow]Períodos válidos: {', '.join(VALID_PERIODS)}[/yellow]")
                    console.print("[cyan]Por favor, ingresa un período válido.[/cyan]")
            
            # Obtiene y valida los nuevos datos
            nuevo_stock_data = obtener_stock_valido(nuevo_symbol, nuevo_period)
            
            if nuevo_stock_data:
                console.print()
                mostrar_info_basica(nuevo_stock_data)
                # Actualiza los datos de la acción en el menú
                stock_data.clear()
                stock_data.update(nuevo_stock_data)
                period = nuevo_period
                symbol = nuevo_stock_data.get('símbolo', 'N/A').upper()
            else:
                # Si la validación falló, vuelve al menú principal
                return False
        
        elif opcion == "3":
            # Vuelve al menú principal
            return False
        
        else:
            console.print("[red]Opción no válida. Por favor selecciona 1, 2 o 3.[/red]")


def mostrar_resumen(stock_data, metricas_seleccionadas=None, mostrar_info_basica=False):
    # Muestra el resumen de la acción con las métricas seleccionadas
    symbol = stock_data.get('símbolo', 'N/A').upper()
    nombre = stock_data.get('nombre', 'N/A')
    sector = stock_data.get('sector', 'N/A')
    industria = stock_data.get('industria', 'N/A')
    pais = stock_data.get('país', 'N/A')
    metricas = stock_data.get('métricas', {})
    
    # Si no se seleccionaron métricas, muestra todas
    if metricas_seleccionadas is None:
        metricas_seleccionadas = ["precios", "volumen", "riesgo"]
    
    # Crea la tabla de métricas
    tabla_info = Table(title=f"Métricas de {symbol}", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    tabla_info.add_column("Métrica", style="cyan", no_wrap=True)
    tabla_info.add_column("Valor", style="green")
    
    # Agrega información básica si se solicita
    if mostrar_info_basica:
        tabla_info.add_row("Nombre", nombre)
        tabla_info.add_row("Símbolo", symbol)
        tabla_info.add_row("Sector", sector)
        tabla_info.add_row("Industria", industria)
        tabla_info.add_row("País", pais)
        if metricas:
            tabla_info.add_row("", "")
    
    # Agrega las métricas seleccionadas
    if metricas:
        # Métricas de precios
        if "precios" in metricas_seleccionadas:
            tabla_info.add_row("", "")
            tabla_info.add_row("[bold]Precios[/bold]", "")
            
            precio = metricas.get('precio', 0.0)
            cambio = metricas.get('cambio', 0.0)
            cambio_porcentual = metricas.get('cambioPorcentual', 0.0)
            maxima_ganancia = metricas.get('maximaGanancia', 0.0)
            maxima_perdida = metricas.get('maximaPerdida', 0.0)
            
            tabla_info.add_row("Precio Actual", f"${precio:.2f}")
            
            # Calcula el precio anterior a partir del cambio
            precio_anterior = precio - cambio if cambio != 0 else precio
            if precio_anterior > 0:
                tabla_info.add_row("Precio Anterior", f"${precio_anterior:.2f}")
            
            # Muestra el cambio con color (verde si sube, rojo si baja)
            color_cambio = "green" if cambio >= 0 else "red"
            tabla_info.add_row("Cambio", f"[{color_cambio}]{cambio:+.2f} ({cambio_porcentual*100:+.2f}%)[/{color_cambio}]")
            tabla_info.add_row("Precio Máximo", f"${maxima_ganancia:.2f}")
            tabla_info.add_row("Precio Mínimo", f"${maxima_perdida:.2f}")
        
        # Métricas de volumen
        if "volumen" in metricas_seleccionadas:
            volumen = metricas.get('volumen', 0.0)
            volumen_promedio = metricas.get('volumenPromedio', 0.0)
            volumen_total = metricas.get('volumenTotal', 0.0)
            
            tabla_info.add_row("", "")
            tabla_info.add_row("[bold]Volumen[/bold]", "")
            tabla_info.add_row("Volumen Actual", f"{volumen:,.0f}")
            tabla_info.add_row("Volumen Promedio", f"{volumen_promedio:,.0f}")
            tabla_info.add_row("Volumen Total", f"{volumen_total:,.0f}")
        
        # Métricas de riesgo
        if "riesgo" in metricas_seleccionadas:
            cambio_porcentual = metricas.get('cambioPorcentual', 0.0)
            volatilidad = metricas.get('volatilidad', 0.0)
            ratio_sharpe = metricas.get('ratioSharpe', 0.0)
            
            tabla_info.add_row("", "")
            tabla_info.add_row("[bold]Rendimientos y Riesgo[/bold]", "")
            
            # Muestra el retorno diario con color
            color_retorno = "green" if cambio_porcentual >= 0 else "red"
            tabla_info.add_row("Retorno Diario", f"[{color_retorno}]{cambio_porcentual*100:+.2f}%[/{color_retorno}]")
            
            # Volatilidad (desviación estándar de precios)
            tabla_info.add_row("Volatilidad (Desv. Est.)", f"${volatilidad:.2f}")
            
            # Ratio de Sharpe
            tabla_info.add_row("Sharpe Ratio", f"{ratio_sharpe:.2f}")
    
    console.print(tabla_info)


@app.command()
def info(
    symbol = typer.Argument(..., help="Símbolo de la acción (e.g., AAPL, MSFT, TSLA)"),
    period = typer.Option("1mo", "--period", "-p", help="Período de tiempo: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
):
    # Comando para obtener información de una acción directamente
    bienvenida()
    console.print()
    
    # Valida el argumento del período
    if not validar_periodo(period):
        console.print(f"[red]Error: Período '{period}' no es válido.[/red]")
        console.print(f"[yellow]Períodos válidos: {', '.join(VALID_PERIODS)}[/yellow]")
        raise typer.Exit(code=1)
    
    # Obtiene y valida los datos de la acción
    stock_data = obtener_stock_valido(symbol, period)
    
    if stock_data:
        console.print()
        # Muestra primero la información básica
        mostrar_info_basica(stock_data)
        
        # Muestra el menú para interactuar con la acción
        menu_stock_actual(stock_data, period)


def ejecutar_menu():
    # Menú principal interactivo de la aplicación
    bienvenida()
    console.print()
    
    while True:
        console.print("\n[bold cyan]Menú Principal[/bold cyan]")
        console.print("1. Buscar información de una acción")
        console.print("2. Ayuda: Cómo encontrar símbolos de acciones")
        console.print("3. Salir")
        
        opcion = typer.prompt("\nSelecciona una opción", default="1")
        
        if opcion == "1":
            # Pide el símbolo y período de la acción
            symbol = typer.prompt("Ingresa el símbolo de la acción (e.g., AAPL, MSFT, TSLA)")
            
            # Valida el período con bucle de reintento
            while True:
                period = typer.prompt(
                    "Período de datos históricos", 
                    default="1mo",
                    show_default=True
                )
                if validar_periodo(period):
                    break
                else:
                    console.print(f"[red]Error: Período '{period}' no es válido.[/red]")
                    console.print(f"[yellow]Períodos válidos: {', '.join(VALID_PERIODS)}[/yellow]")
                    console.print("[cyan]Por favor, ingresa un período válido.[/cyan]")
            
            # Obtiene y valida los datos
            stock_data = obtener_stock_valido(symbol, period)
            
            if stock_data:
                console.print()
                # Muestra primero la información básica
                mostrar_info_basica(stock_data)
                
                # Muestra el menú para la acción actual
                cambiar_stock = menu_stock_actual(stock_data, period)
                
                if not cambiar_stock:
                    # El usuario eligió volver al menú principal
                    continue
        
        elif opcion == "2":
            mostrar_ayuda()
        
        elif opcion == "3":
            console.print("[green]¡Hasta luego![/green]")
            break
        else:
            console.print("[red]Opción no válida. Por favor selecciona 1, 2 o 3.[/red]")


@app.command()
def ayuda():
    # Comando para mostrar la ayuda
    bienvenida()
    mostrar_ayuda()

@app.command()
def menu():
    # Comando para ejecutar el menú interactivo
    ejecutar_menu()

if __name__ == "__main__":
    ejecutar_menu()
