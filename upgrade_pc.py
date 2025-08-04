import asyncio
import httpx
import re
import gspread
import telegram
import os
import json  # Import necessário para ler as credenciais da variável de ambiente
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# =============== CARREGA VARIÁVEIS DE AMBIENTE ===============
# No Railway, as variáveis são carregadas automaticamente, mas load_dotenv() não causa problemas.
load_dotenv()

# =============== CONFIGURAÇÃO GOOGLE SHEETS (VERSÃO PARA RAILWAY) ===============
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Pega o CONTEÚDO do JSON da variável de ambiente do Railway
gcp_credentials_json_str = os.getenv("GCP_CREDENTIALS_JSON")

if not gcp_credentials_json_str:
    # Esta exceção irá parar o script se a variável de credenciais não for encontrada
    raise ValueError(
        "ERRO CRÍTICO: A variável de ambiente GCP_CREDENTIALS_JSON não foi definida no Railway!"
    )

# Converte a string JSON em um dicionário Python
gcp_credentials_dict = json.loads(gcp_credentials_json_str)

# Autentica usando o dicionário em vez de um arquivo
creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_credentials_dict, scope)
client = gspread.authorize(creds)

GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME_UPGRADE")
GOOGLE_SHEETS_WORKSHEET_UPGRADE = os.getenv("GOOGLE_SHEETS_WORKSHEET_UPGRADE")
sheet = client.open(GOOGLE_SHEETS_NAME).worksheet(GOOGLE_SHEETS_WORKSHEET_UPGRADE)


# =============== CONFIGURAÇÃO TELEGRAM ===============
bot_token = os.getenv("TELEGRAM_BOT_TOKEN_UPGRADE")
chat_id = os.getenv("TELEGRAM_CHAT_ID_UPGRADE")
bot = telegram.Bot(token=bot_token)


# =============== LISTA DE ITENS ===============
# Sua lista de produtos completa
itens = [
    #
    # 🎮 GPUs
    {
        "nome": "RX 9060 XT 16GB",
        "preco_alvo": 2999,
        "urls": [
            "https://www.kabum.com.br/produto/870973/placa-de-video-xfx-rx-9060-xt-oc-amd-radeon-16gb-gddr6-128bits-20-gbps-triple-fan-rdna-4-rx-96ts316b7",
            "https://www.amazon.com.br/PowerColor-Hellhound-Radeon-9060-GDDR6/dp/B0F9QK63KR/ref=sr_1_31?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dib=eyJ2IjoiMSJ9.cuxXWFsB6IE3yLD6TNBFMX-6F9XqB_yFxNgsm9pZxCt456E9Gkty70VRyfj_pn2GR68xffkLkW2T6ZMMltOeouc9blMG3FETj7Cg887hKkJNH8NNe8R9iv4zYldLMVM1wkwoaVoPdafA5BVmPEwXgb7TcCc0taydOhdO1Hzhrt1uVZhitVeoAj2awCw7XAcXdCKU6eKR8fZ667cVdj2nL7lh5elvgkB51lqsDEsbVZJ4TwQXs2E-38KHZVp6rUqZ0BFBaGmH34_D4Mmi3E3Ygl0ufZ-jpV2m4y7puy8l2KE.aE3e9s-LphWsnAtCZ2y0PJ_LQ6hgLbg4eHQes7xG3VU&dib_tag=se&keywords=RX+9070+16GB&qid=1754305663&sr=8-31&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147",
        ],
    },
    {
        "nome": "RX 9070 16GB",
        "preco_alvo": 3999,
        "urls": [
            "https://www.kabum.com.br/produto/690385/placa-de-video-asus-prime-rx-9070-xt-o16g-amd-radeon-16gb-gddr6-axial-tech-opengl-4-6-90yv0l71-m0na00",
            "https://www.amazon.com.br/ASRock-gr%C3%A1fica-Accelerators-Graphics-Deflecting/dp/B0DTTGMFK3/ref=sr_1_45?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dib=eyJ2IjoiMSJ9.cuxXWFsB6IE3yLD6TNBFMX-6F9XqB_yFxNgsm9pZxCt456E9Gkty70VRyfj_pn2GR68xffkLkW2T6ZMMltOeouc9blMG3FETj7Cg887hKkJNH8NNe8R9iv4zYldLMVM1wkwoaVoPdafA5BVmPEwXgb7TcCc0taydOhdO1Hzhrt1uVZhitVeoAj2awCw7XAcXdCKU6eKR8fZ667cVdj2nL7lh5elvgkB51lqsDEsbVZJ4TwQXs2E-38KHZVp6rUqZ0BFBaGmH34_D4Mmi3E3Ygl0ufZ-jpV2m4y7puy8l2KE.aE3e9s-LphWsnAtCZ2y0PJ_LQ6hgLbg4eHQes7xG3VU&dib_tag=se&keywords=RX+9070+16GB&qid=1754305737&sr=8-45",
        ],
    },
    # 🖥️ Monitores QHD/WQHD
    {
        "nome": 'Samsung Odyssey G5 27" QHD 165Hz',
        "preco_alvo": 1199,
        "urls": [
            "https://www.kabum.com.br/produto/713377/monitor-gamer-curvo-samsung-odyssey-g5-27-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls27cg552elmzd",
            "https://www.amazon.com.br/Monitor-Gamer-Samsung-Odyssey-G5/dp/B0DWQK1Q8S/ref=sr_1_1_sspa?crid=1GSK90EHF8NBB&dib=eyJ2IjoiMSJ9.dB84mEHTo9Qyq9FugaLoLO80C-Yt7VCRtBPlkNnBZOrAhbjbDcfYFdZFMQGFRWQrXu12mZPPdx_gXIRp4YnUzwBo93FxyWYf6EsLUOCByHVUarg3FW1szyX8MxsUpi51NuNH3h7zHiLC-cGS67JLcJhwH2K1HLNLv7KUUPrpdM8jTpAliF0R4c_351wsTAFP4LaZBJ5HAjqfECnDzOPj2yNLrBp1mLwrfgkQqBagF4wLpnAsXDeSXMwCEJ6agmXE7fW3MKacAotR1Gz5Vf9uzbodUNEB1wi4LqTG9tmdJ8A.PdYalXBFJuW30SAmmvVnt0P9CQcig4Ac7vzlxyztx8Q&dib_tag=se&keywords=odyssey+g5+27&qid=1754305831&sprefix=odyssey+g5+27%2Caps%2C193&sr=8-1-spons&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 32" QHD 165Hz',
        "preco_alvo": 1519,
        "urls": [
            "https://www.kabum.com.br/produto/713376/monitor-gamer-curvo-samsung-odyssey-g5-32-qhd-165hz-1ms-hdr10-freesync-hdmi-e-dp-preto-ls32cg552elmzd",
            "https://www.amazon.com.br/Monitor-Gamer-Samsung-Odyssey-G5/dp/B0DWQNS8TN/ref=sr_1_5?crid=1171OIEIGX8Y8&dib=eyJ2IjoiMSJ9.pl4I6RRqVzd-TrJYXMRIk4fJ5nc0IXznNJgrKa7S38h7lLtYMuDUOmHMqPjOJwye0H9WZjgPf9CWET18EWrykb2TS-JAygOR3i8zG4aRMPr97dGkF-9oq5oIfwLtGEbBVr9npzTUxeY6w0eGYe-JCMEOe9xQpfaNG4jRx88-mECzrery33c_ngyTO5SzJQQpewIqrfSC9dROILcsiEj6_EqsHSI3h_JUI6_6wrqyIhWBW9Z5xZesSEvxGV8Yp1UywIa22AlJHcyBj3CQUnVq5iPEDvPptmolfFAXIrWj49M.FbneabsgKgoDXHe7JnkKdrrkstpzmJ1pQFZkBOTslvY&dib_tag=se&keywords=odyssey+g5+32&qid=1754305879&sprefix=odyssey+g5+32%2Caps%2C219&sr=8-5"
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
            "https://www.amazon.com.br/MONITOR-LG-ULTRAGEAR-32GN600-32-165HZ/dp/B0DJQ11WXY/ref=sr_1_4?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3F6U3BXZRHVMP&dib=eyJ2IjoiMSJ9.9EjNkQxzx8T_oFUKjHZokk73cX3mfLToVRsGaA1X5JTLHIDgNMA85Ai4-m0HRjdM6OBrmS6eNwYWMSnkMbtOlEUsNyhbXyhtF_eL2eqF_78hEfm4a4xFc9RMaO9R4kLxkv0zuJyc3c5Qt0o3QXsjGBUyH3UozGmBzJv4j3OQDs-VOG70vBMH4PBFewsHuCXFUn5e1wZzmDVCzHvkH4eFM8I7tj6iNvHOk4QZpqSAN4cQadp-Ty0dVpEf7WZpc-mePe5Sn7RsGPiTuMEsM7cT-HYWXrZJeOAjjoGpn0IFdlE.LxCGKj_fhKxD1MKT21v7fBr_3GiZx-lmWdJ4MvHm9ac&dib_tag=se&keywords=lg+ultragear+27+%22qhd+144hz%5C%22%22&qid=1754305964&sprefix=lg+ultragear+27%22+qhd+144hz%2Caps%2C242&sr=8-4&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147"
        ],
    },
    {
        "nome": 'Samsung Odyssey G5 34" WQHD 100Hz',
        "preco_alvo": 1799,
        "urls": [
            "https://www.amazon.com.br/Monitor-Samsung-Odyssey-ultrawide-Freesync/dp/B0D3J76C63/ref=sr_1_2?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=3VJCGNI77ZOS&dib=eyJ2IjoiMSJ9.D0YqVvPBqw0BlzN78E0_GO_vFou7j10TmrhRgjM_2EpF0We9L9E2AdnLmbX3KNHaYjbyvyz79bOoi1sC-lzoMcA9jJxJ5oXegD5SbK_aTGCe_NgS3z9s5yzJLgcS70FmYr1j9Jpmo0P_q_DWzHWhVHT8i5sYWB-oE4tWt2OtaFiSNHbNb6vCiekOUCYpJ_1jZ20KbJKvp4SWkOtMhUHu-EzjBbuKSxGl9VyEWWAVE__3__foeENLHMsMZUnSolYX1TVp-Nina1WGHhW3vP_kro45qXpprNcWki-Z1RLk6fk.VSGoXk9ENHuk5h1Q_upL6k_z_s5yznsGxRBwuFCtywk&dib_tag=se&keywords=samsung+odyssey+g5+34+%22wqhd+100hz&qid=1754306036&sprefix=samsung+odyssey+g5+34%22+wqhd+100hz%2Caps%2C153&sr=8-2&ufe=app_do%3Aamzn1.fos.25548f35-0de7-44b3-b28e-0f56f3f96147",
        ],
    },
    },
    # 💾 Memórias RAM DDR4 2x16GB
    {
        "nome": "Corsair Vengeance 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/652119/memoria-de-desktop-corsair-vengeance-rgb-pro-32gb-2x16gb-ddr4-3200-pc4-25600-c16-branca-cmw32gx4m2e3200c16w",
            "https://www.amazon.com.br/Corsair-Mem%C3%B3ria-computador-VENGEANCE-3200MHz/dp/B07RW6Z692/ref=sr_1_4_mod_primary_new?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=99L1700AVTJO&dib=eyJ2IjoiMSJ9.r1s1DniWVhlIH3HskYkjTc9uUyYy6XX0pxSI5seZPE5y7ekbhDpv7YD3KhLW8K1vuVZga0vcr-rBtUqY9Az1Ki4kaLaK3sWnDv7Ka9__UQz1TB5ZCx44XVH-GY-pT2hYJIArBWGd5_a8kbovc_LFWRyXn6ByCxAbEbUsRnzZL9ZG9AN4Gbfd2SgijAqg4s2JlTPWnZZMG9PSnACGKY6tkHpomJzdk4x-09YBu7ub-B4AB3SxfnjtyQLH4TyxogvAKm0NUv8wf5c67Yb_CxN3l2smhMqCaWkDWlgT0Wx2lAc.Xp7pjl0m7xO_UgCNkvAbaI8WrjVfyptiMxnQ9R8e2w4&dib_tag=se&keywords=Corsair+Vengeance+2x16GB+3200+CL16&qid=1754306115&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sprefix=corsair+vengeance+2x16gb+3200+cl16%2Caps%2C140&sr=8-4"
        ],
    },
    {
        "nome": "Patriot Viper Steel 2x16GB 3200 CL16",
        "preco_alvo": 389,
        "urls": [
            "https://www.amazon.com.br/Patriot-Viper-Elite-DDR4-3200/dp/B0957V957P/ref=sr_1_7?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2M5EJ7AVGGT81&dib=eyJ2IjoiMSJ9.adt1hnFkNKgPpKAOase-4RPZ8cCNKBh-rh794h7icdPMbrwpVLAWhr2YaW5rLYU2uEmGWtq4CX25nNSJoJ5GIdIkJk8sAAMC2Ol3-NcjJT-5-bx5HBDBNGtTqdm41y70boQ4cktJfPpm9qJEXXc3FwiCeT6Gx7Uf4kLWEZ1vDl8mzDm2_v_crh6Y6YxoJlX_EzlSa-kxFWhnqRHp-PZxvnqn7b7Fqo6Dpaw4zCeyIwoU47pP-M-uw22yMHGIevz4O6CQowiYse4F0ryYjMoh1MisGqRnsYu8cd191qM1C4c.J5U6nQrcn4POu33-waJWHgQwhnv6zahiCG1cKosi4Lo&dib_tag=se&keywords=Patriot%2BViper%2BSteel%2B2x16GB%2B3200%2BCL16&qid=1754306155&sprefix=patriot%2Bviper%2Bsteel%2B2x16gb%2B3200%2Bcl16%2Caps%2C146&sr=8-7&th=1"
        ],
    },
    {
        "nome": "Kingston Fury Beast 2x16GB 3200 CL16",
        "preco_alvo": 399,
        "urls": [
            "https://www.kabum.com.br/produto/616568/memoria-ram-kingston-fury-beast-expo-32gb-2x16gb-6000mt-s-ddr5-dimm-cl30-preto-kf560c30bbek2-32",
            "https://www.amazon.com.br/KF432C16BBK2-32-mem%C3%B3rias-3200Mhz-desktop/dp/B097K2WKZW/ref=sr_1_15?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=1L18LYO7CRL7N&dib=eyJ2IjoiMSJ9.LVNv0eYjyDO5OyGV3v3kCLlWfqfTyxu9dr-dRk44eqihsYqukZ6rKm6rkVuclsaAhffmY0nYELjwINp0pjhtR-bbg6U4WYNLZqAYecaNqvI1631PO8enWlUPioYXkesku0cH6Q6nsAwo95hehErKctyqTTnCTMk3LgeFPFXR4E8fGVQYKB8YFJkjn0df2VYgskgmK5cNoAZ2Q4CaH1c2KnFI3fMOoGZ9XuE442-8WxuPRrV7QpVS4dmSsE_N1iJ8Ehy4b1o16UR6qL4p6-Cu98dqDL2EFP8sXRuBFynwWZg.Fzz6cMwSKP1znWw8Tdo0TmCZLp0k1auF0m43R4hC3Ik&dib_tag=se&keywords=Kingston+Fury+Beast+2x16GB+3200+CL16&qid=1754306269&sprefix=kingston+fury+beast+2x16gb+3200+cl16%2Caps%2C1412&sr=8-15"
        ],
    },
    # 🖱️ Fans ARGB
    {
        "nome": "Lian Li UNI FAN SL-INF 120 kit 4",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/519402/kit-de-fan-lian-li-uni-fan-sl120-redragon-spec-preto?srsltid=AfmBOooNCWB9BiUw_l-91zAMHtZzIhuJ7Pg6wq2JoVK-d7Mk4pD_-xCbcpA",
            "https://www.amazon.com.br/KIT-GAMER-PRETO-FANS-UF-SL120-3B/dp/B0CSDZ6QMT"
        ],
    },
    {
        "nome": "DeepCool FK120 kit 3",
        "preco_alvo": 239,
        "urls": [
            "https://www.terabyteshop.com.br/produto/22425/kit-fan-com-3-unidades-deepcool-fc120-rgb-120mm-black-r-fc120-bkamn3-g-1?srsltid=AfmBOoqHahQBNsTsYY5WN0zsAp-ahYIZhR4m45dCNhO2-NlMtjyP3fZQQUs",
        ],
    },
    {
        "nome": "Cooler Master Mobius kit 3",
        "preco_alvo": 479,
        "urls": [
            "https://produto.mercadolivre.com.br/MLB-3363490221-kit-3-cooler-master-mobius-120p-argb-2400-rpm-alta-presso-_JM?matt_tool=18956390&utm_source=google_shopping&utm_medium=organic",
        ],
    },
    # 🖥️ Gabinetes brancos ARGB
    {
        "nome": "Lian Li Lancool 215 White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/346385/gabinete-gamer-lancool-215-2x-fans-argb-laterais-em-vidro-temperado-branco-lancool-215-w-white?srsltid=AfmBOorhA36k8yP3YKVW6ZzlL5woGGyn6l6VkzDuFWU8PRDUUVKqakF1L4M",
            "https://www.amazon.com.br/Lian-Li-GABINETE-LANCOOL-215/dp/B09MLY1VKC"
        ],
    },
    {
        "nome": "NZXT H510 Flow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/446560/gabinete-nzxt-h5-flow-rgb-edition-mid-tower-atx-lateral-em-vidro-temperado-cooler-fan-rgb-branco-cc-h51fw-r1?srsltid=AfmBOopjEI1Horq31HMW1_BZ54rwxusdzenGEI_HvgvEETJ16Yrhk9v1tsM",
            "https://www.amazon.com.br/NZXT-H5-Flow-RGB-Branco/dp/B0BQSL8JG2"
        ],
    },
    {
        "nome": "Corsair 4000D Airflow White",
        "preco_alvo": 499,
        "urls": [
            "https://www.kabum.com.br/produto/657434/gabinete-gamer-corsair-frame-4000d-rs-mid-tower-lateral-em-vidro-branco-cc-9011291-ww?srsltid=AfmBOorGuUjsM4Fo8dT81037SHNNBFzYBO_E_ctn2g37c_woihIGcpqUyP0",
        ],
    },
    # 🔌 Placas-Mãe
    {
        "nome": "ASUS ROG Strix B550-F Gaming WiFi",
        "preco_alvo": 899,
        "urls": [
            "https://www.kabum.com.br/produto/264899/placa-mae-asus-rog-strix-b550-f-gaming-ii-amd-am4-aura-sync-rgb-atx-ddr4-wi-fi-preto-90mb19v0-m0eay0?srsltid=AfmBOorQu2uEaesRcNxIbLkSfH3cjzbq2o_lOX4fSSr1kl-3dQ9B7wW1NNQ",
            "https://www.terabyteshop.com.br/produto/20306/placa-mae-asus-rog-strix-b550-f-gaming-wi-fi-ii-chipset-b550-amd-am4-atx-ddr4-90mb19v0-m0eay0?srsltid=AfmBOoqAlwO3bb_PM2tIuIgmzTBe_WOkD-vtrtXNsVI-V6gGlRFBKRoKrro"
        ],
    },
    {
        "nome": "MSI B550 TOMAHAWK",
        "preco_alvo": 1300,
        "urls": [
            "https://www.amazon.com.br/MSI-MAG-B550-TOMAHAWK-processadores/dp/B089CWDHFZ",
        ],
    },
    {
        "nome": "Gigabyte B550 Aorus Elite V2",
        "preco_alvo": 749,
        "urls": [
            "https://www.kabum.com.br/produto/636782/placa-mae-gigabyte-b550-gaming-x-v2-amd-am4-atx-ddr4-rgb-9mb55gmx2-00-10?srsltid=AfmBOorsDLDAXVxGHgDxXBx5bn1cKeX7B2S7AX3E0u-EgTUjHQMznBfFjKI",
        ],
    },
    # 🖥️ Outros (opcional)
    {
        "nome": "SSD NVMe 1TB Gen4 (Crucial P3, Kingston NV2)",
        "preco_alvo": 289,
        "urls": [
            "https://www.kabum.com.br/produto/621162/ssd-kingston-nv3-1-tb-m-2-2280-pcie-4-0-x4-nvme-leitura-6000-mb-s-gravacao-4000-mb-s-azul-snv3s-1000g?srsltid=AfmBOopsXex41z0sRCbtMoo6eYDiKC3Tqw0Ac6_6A1D4N_Z49y_8P-isYrE",
        ],
    }
]

# =============== FUNÇÕES ASSÍNCRONAS ===============


async def get_price(url: str, client: httpx.AsyncClient) -> float | None:
    """
    Função assíncrona para buscar o preço usando XPath para maior robustez.
    """
    try:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        tree = html.fromstring(r.content)

        xpath_expressions = [
            "//div[.//text()[contains(., 'vista no PIX')]]/h4/text()",
            '//span[contains(@class, "a-price")]/text()',
        ]

        price_text = None
        for expr in xpath_expressions:
            result = tree.xpath(expr)
            if result:
                price_text = result[0].strip()
                print(f"INFO: Preço encontrado com a expressão XPath: {expr}")
                break

        if price_text:
            match = re.search(r"[\d\.,]+", price_text)
            if match:
                price_str = match.group(0)
                price_float = float(price_str.replace(".", "").replace(",", "."))
                return price_float

    except httpx.HTTPStatusError as e:
        print(f"ERRO de status HTTP ao acessar {url}: {repr(e)}")
    except Exception as e:
        print(f"ERRO inesperado ao processar a URL {url}: {repr(e)}")

    return None


async def rastrear():
    """
    Função principal de rastreio, executada pelo agendador.
    """
    print(
        f"--- INICIANDO RASTREIO AGENDADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---"
    )
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    promocao_encontrada = False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    async with httpx.AsyncClient(headers=headers, timeout=20) as client:
        for item in itens:
            print(f"--- Verificando item: {item['nome']} ---")
            for url in item["urls"]:
                if "LINK-DO-PRODUTO-AQUI" in url:
                    print(f"AVISO: Pulando URL de exemplo para '{item['nome']}': {url}")
                    continue

                preco = await get_price(url, client)

                if preco:
                    print(f"  -> Loja: {url.split('/')[2]} | Preço: R$ {preco:.2f}")
                    sheet.append_row([data_hora, item["nome"], preco, url])

                    if preco <= item["preco_alvo"]:
                        msg = (
                            f"🔥 OPORTUNIDADE! 🔥\n\n"
                            f"Produto: {item['nome']}\n"
                            f"Preço: R$ {preco:.2f} (Alvo: R$ {item['preco_alvo']:.2f})\n\n"
                            f"Link: {url}"
                        )
                        await bot.send_message(chat_id=chat_id, text=msg)
                        print(f"ALERTA ENVIADO para {item['nome']}")
                        promocao_encontrada = True
                else:
                    print(f"  -> Preço não encontrado em: {url}")

                await asyncio.sleep(5)

            print("-" * (len(item["nome"]) + 22))

    if not promocao_encontrada:
        msg_status = "Nenhuma promoção localizada desta vez 😥"
        await bot.send_message(chat_id=chat_id, text=msg_status)
        print(
            "INFO: Nenhuma promoção encontrada. Mensagem de status enviada ao Telegram."
        )

    print(
        f"--- RASTREIO AGENDADO FINALIZADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---"
    )


# =============== EXECUÇÃO COM AGENDAMENTO SEMANAL ===============
async def main():
    """
    Função principal que configura e inicia o agendador.
    """
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(rastrear, "interval", hours=24)
    scheduler.start()

    print("✅ Agendador iniciado com sucesso!")
    print("O rastreio será executado automaticamente a cada 24 horas.")
    print("Executando primeira verificação em 30 segundos...")
    print("Mantenha este serviço rodando para o agendador funcionar.")
    print("Pressione Ctrl+C nos logs para reiniciar, se necessário.")

    # Executa uma verificação inicial após 30 segundos
    await asyncio.sleep(30)
    await rastrear()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nAgendador finalizado.")


if __name__ == "__main__":
    asyncio.run(main())
