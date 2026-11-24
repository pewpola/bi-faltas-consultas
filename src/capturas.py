"""
Tira as capturas de tela do painel usadas no relatório e nos slides (pasta figuras/).

Precisa do painel aberto (streamlit run app.py) e do Playwright com o Chromium instalado:
    pip install playwright && playwright install chromium
    python src/capturas.py

Gera duas capturas da página inteira:
- painel_geral.png: o painel sem nenhum filtro;
- painel_combinado.png: bairro Itararé escolhido na lateral + clique em "8 a 15 dias"
  no gráfico de antecedência, o exemplo de filtros combinados do relatório.
"""

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

RAIZ = Path(__file__).resolve().parent.parent
FIGURAS = RAIZ / "figuras"
URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
LARGURA, ALTURA = 1500, 4600   # altura grande para a página inteira caber de uma vez


async def esperar_painel(pagina):
    """Espera o Streamlit terminar de rodar e os gráficos aparecerem."""
    await pagina.wait_for_selector(".js-plotly-plot", timeout=60_000)
    await pagina.wait_for_function(
        "() => !document.querySelector('[data-testid=\"stStatusWidget\"]')", timeout=60_000)
    await pagina.wait_for_timeout(2500)


async def main():
    FIGURAS.mkdir(exist_ok=True)
    async with async_playwright() as p:
        # CHROME_PATH permite apontar para um Chromium já instalado, se a versão do Playwright não bater.
        caminho = os.environ.get("CHROME_PATH")
        navegador = await p.chromium.launch(executable_path=caminho) if caminho else await p.chromium.launch()
        pagina = await navegador.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=2)
        await pagina.goto(URL)
        await esperar_painel(pagina)
        await pagina.screenshot(path=FIGURAS / "painel_geral.png")

        # Filtro da lateral: bairro Itararé
        campo = pagina.get_by_role("combobox", name="Bairro da unidade")
        await campo.click()
        await campo.fill("Itararé")
        await pagina.get_by_role("option", name="Itararé").click()
        await pagina.keyboard.press("Escape")
        await esperar_painel(pagina)

        # Clique na barra "8 a 15 dias" (quarta barra do primeiro gráfico)
        barras = pagina.locator(".js-plotly-plot").first.locator("g.point path")
        caixa = await barras.nth(3).bounding_box()   # o Plotly cobre as barras com uma camada de clique,
        await pagina.mouse.click(caixa["x"] + caixa["width"] / 2, caixa["y"] + caixa["height"] / 2)  # então clica pela posição
        await esperar_painel(pagina)
        await pagina.screenshot(path=FIGURAS / "painel_combinado.png")
        await navegador.close()
    print("Capturas gravadas em figuras/")


if __name__ == "__main__":
    asyncio.run(main())
