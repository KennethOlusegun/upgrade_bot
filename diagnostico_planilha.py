import pandas as pd
import os

# Nome do seu arquivo Excel
filename = 'pc_upgrade - Itens Rastreio.xlsx'

# Lista completa de itens
itens_para_adicionar = [
    # 🎮 GPUs
    {
        "nome": "RX 9060 XT 16GB",
        "preco_alvo": 2999,
        "urls": [
            "https://www.kabum.com.br/produto/870973/placa-de-video-xfx-rx-9060-xt-oc-amd-radeon-16gb-gddr6-128bits-20-gbps-triple-fan-rdna-4-rx-96ts316b7",
            "https://www.pichau.com.br/placa-de-video-xfx-radeon-rx-9060-xt-mercury-oc-gaming-edition-16gb-gddr6-128-bit-rx-96tmercb9",
        ],
    },
    {
        "nome": "RX 9070 16GB",
        "preco_alvo": 3999,
        "urls": [
            "https://www.kabum.com.br/produto/690385/placa-de-video-asus-prime-rx-9070-xt-o16g-amd-radeon-16gb-gddr6-axial-tech-opengl-4-6-90yv0l71-m0na00",
            "https://www.pichau.com.br/placa-de-video-xfx-radeon-rx-9070-xt-mercury-16gb-gddr6-256-bit-rx-97tmercb9",
        ],
    },
    # 🖥️ Monitores QHD/WQHD
    {
        "nome": 'Samsung Odyssey G5 27" QHD 165Hz',
        "preco_alvo": 1199,
        "urls": [
            "https://www.kabum.com.br/produto/713377/monitor-gamer-curvo-samsung-odyssey-g5-27-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls27cg552elmzd",
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 32" QHD 165Hz',
        "preco_alvo": 1519,
        "urls": [
            "https://www.kabum.com.br/produto/713376/monitor-gamer-curvo-samsung-odyssey-g5-32-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls32cg552elmzd",
        ],
    },
    {
        "nome": 'LG Ultragear 27" QHD 180Hz',
        "preco_alvo": 1299,
        "urls": [
            "https://www.kabum.com.br/produto/620992/monitor-gamer-lg-ultragear-27-fhd-ips-180hz-1ms-gtg-hdr10-displayport-e-hdmi-g-sync-freesync-preto-27gs60f-b",
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 34" WQHD 100Hz',
        "preco_alvo": 1799,
        "urls": [
            "https://www.kabum.com.br/produto/613318/monitor-gamer-curvo-samsung-odyssey-g5-34-wqhd-ultrawide-165hz-1ms-hdmi-e-dp-freesync-premium-preto-lc34g55twwlmzd",
        ],
    },
    # 💾 Memórias RAM DDR4 2x16GB
    {
        "nome": "Corsair Vengeance 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/110828/memoria-ram-corsair-vengeance-lpx-32gb-2x16gb-3200mhz-ddr4-cl16-black-cmk32gx4m2e3200c16",
        ],
    },
    {
        "nome": "Patriot Viper Steel 16GB 3200 CL16",
        "preco_alvo": 389,
        "urls": [
            "https://www.kabum.com.br/produto/381082/memoria-patriot-viper-steel-rgb-16gb-3200mhz-ddr4-cl18-udimm-pvsr416g320c8",
        ],
    },
    {
        "nome": "Kingston Fury Beast 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/193569/memoria-ram-kingston-fury-beast-32gb-2x16gb-3600mhz-ddr4-cl18-preto-kf436c18bbk2-32",
        ],
    },
    # 🖱️ Fans ARGB
    {
        "nome": "Lian Li UNI FAN SL-INF 120 kit 4",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/894985/fan-gamer-lian-li-uni-fan-sl-wireless-120-argb-branco?srsltid=AfmBOooCNG4pLMqXO5W6yrrivQPqU0_79By42CgZXfsDJ0R9BLlLpEprakw",
        ],
    },
    {
        "nome": "DeepCool FK120 kit 3",
        "preco_alvo": 239,
        "urls": [
            "https://www.kabum.com.br/produto/479414/kit-fan-deepcool-fk120-120mm-preto-com-3-unidades-r-fk120-bknpf3-g-1",
        ],
    },
    {
        "nome": "Cooler Master Mobius kit 3",
        "preco_alvo": 479,
        "urls": [
            "https://www.kabum.com.br/produto/882982/kit-3-fan-cooler-master-mobius-120p-120mm-argb-e-controlador",
        ],
    },
    # 🖥️ Gabinetes brancos ARGB
    {
        "nome": "Lian Li Lancool 215 White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/346385/gabinete-gamer-lancool-215-2x-fans-argb-laterais-em-vidro-temperado-branco-lancool-215-w-white",
        ],
    },
    {
        "nome": "Lian Li Lancool 216 White ARGB",
        "preco_alvo": 599,
        "urls": [
            "https://www.kabum.com.br/produto/430153/gabinete-gamer-lancool-216-argb-mid-tower-e-atx-lateral-em-vidro-temperado-3x-cooler-fan-branco-lancool-216rw-white",
        ],
    },
    {
        "nome": "NZXT H510 Flow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/110027/gabinete-gamer-nzxt-h510-mid-tower-com-fan-lateral-em-vidro-branco-ca-h510b-w1",
        ],
    },
    {
        "nome": "Corsair 4000D Airflow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/657436/gabinete-gamer-corsair-4000d-rs-argb-mid-tower-lateral-em-vidro-com-3x-fans-rs-argb-branco-cc-9011297-ww",
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
            "https://www.kabum.com.br/produto/272356/ssd-kingston-fury-renegade-1tb-m-2-2280-pcie-4-0-x4-nvme-leitura-7300-mb-s-gravacao-6000-mb-s-compativel-com-ps5-sfyrs-1000g",
        ],
    },
    {
        "nome": "SSD NVMe 1TB Gen4 (Crucial P5 Plus, WD SN770)",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/272356/ssd-kingston-fury-renegade-1tb-m-2-2280-pcie-4-0-x4-nvme-leitura-7300-mb-s-gravacao-6000-mb-s-compativel-com-ps5-sfyrs-1000g",
        ],
    },
]

def diagnosticar_e_atualizar():
    print(f"--- INICIANDO DIAGNÓSTICO ---")
    print(f"Verificando arquivo: '{filename}'")
    
    colunas = ['Nome', 'Preco Alvo', 'URL']
    
    try:
        df_existente = pd.read_excel(filename)
        urls_existentes = set(df_existente['URL'])
        print(f"LEITURA: {len(urls_existentes)} URLs existentes foram encontradas na planilha.")
    except FileNotFoundError:
        print("LEITURA: Arquivo não encontrado. Um novo será criado.")
        df_existente = pd.DataFrame(columns=colunas)
        urls_existentes = set()
    except Exception as e:
        print(f"ERRO DE LEITURA: Ocorreu um erro ao ler a planilha: {e}")
        return

    novas_linhas = []
    
    # --- PONTO DE DIAGNÓSTICO ---
    total_de_itens = len(itens_para_adicionar)
    print(f"PROCESSAMENTO: A lista no script tem um total de {total_de_itens} produtos.")
    print("--- INICIANDO LOOP ---")

    for i, item in enumerate(itens_para_adicionar):
        # --- Imprime o progresso para cada item ---
        print(f"  Item {i+1}/{total_de_itens}: Verificando '{item['nome']}'...")
        
        for url in item.get('urls', []):
            if url not in urls_existentes:
                novas_linhas.append({
                    'Nome': item['nome'],
                    'Preco Alvo': item['preco_alvo'],
                    'URL': url
                })
                urls_existentes.add(url)

    print("--- FIM DO LOOP ---")

    if novas_linhas:
        print(f"ESCRITA: {len(novas_linhas)} novas linhas prontas para serem adicionadas.")
        df_novas = pd.DataFrame(novas_linhas)
        df_final = pd.concat([df_existente, df_novas], ignore_index=True)
        
        try:
            df_final.to_excel(filename, index=False)
            print(f"SUCESSO: {len(novas_linhas)} novas linhas foram salvas em '{filename}'.")
        except Exception as e:
            print(f"ERRO DE ESCRITA: Ocorreu um erro ao salvar a planilha: {e}")
    else:
        print("Nenhum item novo para adicionar. A planilha já está atualizada.")
    
    print("--- DIAGNÓSTICO FINALIZADO ---")

if __name__ == "__main__":
    diagnosticar_e_atualizar()