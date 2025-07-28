import pandas as pd
import os

# Nome do seu arquivo Excel
filename = 'pc_upgrade - Itens Rastreio.xlsx'

# CERTIFIQUE-SE DE QUE ESTA LISTA ESTÁ COMPLETA
# A lista abaixo contém todos os 23 itens.
itens_para_adicionar = [
    # 🎮 GPUs
    {
        "nome": "RX 9060 XT 16GB",
        "preco_alvo": 2999,
        "urls": [
            "https://www.kabum.com.br/produto/870973/placa-de-video-xfx-rx-9060-xt-oc-amd-radeon-16gb-gddr6-128bits-20-gbps-triple-fan-rdna-4-rx-96ts316b7",
            "https://www.pichau.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "RX 9070 16GB",
        "preco_alvo": 3999,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
            "https://www.pichau.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🖥️ Monitores QHD/WQHD
    {
        "nome": 'Samsung Odyssey G5 27" QHD 165Hz',
        "preco_alvo": 1199,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 32" QHD 165Hz',
        "preco_alvo": 1519,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": 'LG Ultragear 27" QHD 144Hz',
        "preco_alvo": 1299,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": 'LG Ultragear 32" QHD 165Hz',
        "preco_alvo": 1399,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 34" WQHD 100Hz',
        "preco_alvo": 1799,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": 'Acer Nitro 27" WQHD 320Hz',
        "preco_alvo": 1899,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 💾 Memórias RAM DDR4 2x16GB
    {
        "nome": "Corsair Vengeance 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Patriot Viper Steel 2x16GB 3200 CL16",
        "preco_alvo": 389,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Kingston Fury Beast 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🖱️ Fans ARGB
    {
        "nome": "Lian Li UNI FAN SL-INF 120 kit 4",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "DeepCool FK120 kit 3",
        "preco_alvo": 239,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Cooler Master Mobius kit 3",
        "preco_alvo": 479,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🖥️ Gabinetes brancos ARGB
    {
        "nome": "Lian Li Lancool 215 White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Lian Li Lancool 216 White ARGB",
        "preco_alvo": 599,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "NZXT H510 Flow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Corsair 4000D Airflow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Corsair 4000D Airflow",
        "preco_alvo": 530,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🌡️ Cooler
    {
        "nome": "Rise Mode Z240 Frost White",
        "preco_alvo": 169,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    # 🖥️ Outros (opcional)
    {
        "nome": "SSD NVMe 1TB Gen3 (Crucial P3, Kingston NV2)",
        "preco_alvo": 289,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "SSD NVMe 1TB Gen4 (Crucial P5 Plus, WD SN770)",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
    {
        "nome": "Fonte Corsair RM650e",
        "preco_alvo": 429,
        "urls": [
            "https://www.kabum.com.br/produto/LINK-DO-PRODUTO-AQUI",
        ],
    },
]


def atualizar_planilha_excel():
    print(f"Verificando arquivo '{filename}'...")
    
    colunas = ['Nome', 'Preco Alvo', 'URL']
    
    try:
        df_existente = pd.read_excel(filename)
        urls_existentes = set(df_existente['URL'])
        print(f"{len(urls_existentes)} URLs existentes foram encontradas na planilha.")
    except FileNotFoundError:
        print("Arquivo não encontrado. Um novo será criado.")
        df_existente = pd.DataFrame(columns=colunas)
        urls_existentes = set()
    except Exception as e:
        print(f"Ocorreu um erro ao ler a planilha: {e}")
        return

    novas_linhas = []
    for item in itens_para_adicionar:
        for url in item.get('urls', []):
            if url not in urls_existentes:
                novas_linhas.append({
                    'Nome': item['nome'],
                    'Preco Alvo': item['preco_alvo'],
                    'URL': url
                })
                urls_existentes.add(url)

    if novas_linhas:
        df_novas = pd.DataFrame(novas_linhas)
        df_final = pd.concat([df_existente, df_novas], ignore_index=True)
        
        try:
            df_final.to_excel(filename, index=False)
            print(f"Sucesso! {len(novas_linhas)} novas linhas foram adicionadas à planilha '{filename}'.")
        except Exception as e:
            print(f"Ocorreu um erro ao salvar a planilha: {e}")
    else:
        print("Nenhum item novo para adicionar. A planilha já está atualizada.")


if __name__ == "__main__":
    atualizar_planilha_excel()